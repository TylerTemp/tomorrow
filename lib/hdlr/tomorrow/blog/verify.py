import tornado.web
import logging
import json
import re
import time
from passlib.hash import sha256_crypt
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

from .base import EnsureSsl, BaseHandler

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db import User, Article, Message
from lib.tool.mail import Email
from lib.tool.tracemore import get_exc_plus
sys.path.pop(0)

logger = logging.getLogger('tomorrow.blog.verify')


class VerifyHandler(BaseHandler):
    ERROR_EXPIRED = 1
    ERROR_USER_EXISTS = 2
    ERROR_EMAIL_EXISTS = 4
    USER_RE = re.compile(
        r'^[a-zA-Z0-9\u4e00-\u9fa5_\ \-][a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]'
        r'|[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-][a-zA-Z0-9\u4e00-\u9fa5_\ \-]'
        r'|[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]{3,100}$')
    EMAIL_RE = re.compile(r'^[\w\d.+-]+@([\w\d.]+\.)+\w{2,}$')

    PWD_MIN_LEN = 8

    @EnsureSsl(True)
    def get(self, code):
        user = User.init_by_code(unquote(code))
        kwargs = {'error': ''}
        if user.new:
            logger.debug('no user has code %s', code)
            kwargs['error'] = 'nocode'
            return self.render(
                'tomorrow/verify.html',
                **kwargs
            )

        user_info = user.get()
        logger.debug(user_info)
        kwargs['user_name'] = user_info['user']
        kwargs['user_type'] = user_info['type']
        kwargs['user_pwd'] = user_info['pwd']
        kwargs['user_email'] = user_info['email']
        if user_info['user'] is not None:
            kwargs['main_url'] = '/am/%s' % quote(user_info['user'])
        else:
            kwargs['main_url'] = '/am/%s' % quote(user_info['email'])

        if ('expire' in user_info['verify'] and
                time.time() > user_info['verify']['expire']):
            kwargs['error'] = 'expire'
            logger.debug('%s expire' % code)
            return self.render(
                'verify.html',
                **kwargs
            )

        action = user_info['verify']['for']
        if action & User.NEWUSER:
            kwargs.update(self.new_user(user))
        kwargs['change_email'] = (action & User.CHANGEEMAIL)
        kwargs['change_pwd'] = (not user_info['pwd']
                                 or (action & User.CHANGEPWD))
        kwargs['change_user'] = (not user_info['user']
                                 or (action & User.CHANGEUSER))
        kwargs['email'] = user_info['email']
        kwargs['user'] = user_info['user']

        logger.debug(kwargs)

        return self.render(
            'verify.html',
            **kwargs
        )

    def new_user(self, user):
        user_info = user.get()
        verify_info = user_info['verify']

        if user_info['user'] is not None:
            verify_info['for'] &= (~User.NEWUSER)
            if verify_info['for'] == 0:
                user_info.pop('verify')
            user_info['active'] = True
            user.save()
            self.set_user(user_info['user'], user_info['email'],
                          user_info['type'], user_info['active'], temp=True)
            return {'error': 'succeed'}

        return {}

    @EnsureSsl(True)
    # @tornado.web.asynchronous
    # @tornado.gen.coroutine
    def post(self, code=None):
        self.check_xsrf_cookie()
        # validated by get, so raise when unexpected
        user = User.init_by_code(unquote(code))
        assert not user.new

        user_info = user.get()
        verify = user_info['verify']

        # this should not raise
        if 'expire' in verify and verify['expire'] < time.time():
            logger.debug('expired: %s', user)
            self.write(json.dumps({'error': self.ERROR_EXPIRED}))
            self.finish()
            return

        action = verify['for']
        kwargs = {'error': 0}
        # if action & User.NEWUSER:
        #     self.save_new(user)
        all_callbacks = []
        if action & User.CHANGEEMAIL:
            status, callbacks = self.save_email(user)
            all_callbacks.extend(callbacks)
            kwargs['error'] |= status
        if action & User.CHANGEPWD or not user_info['pwd']:
            status, callbacks = self.save_pwd(user)
            all_callbacks.extend(callbacks)
            kwargs['error'] |= status
        if action & User.CHANGEUSER or not user_info['user']:
            status, callbacks = self.save_user(user)
            all_callbacks.extend(callbacks)
            kwargs['error'] |= status

        if kwargs['error'] == 0:
            if verify['for'] == 0:
                user_info.pop('verify')
            user.save()
            self.set_user(user_info['user'],
                          user_info['email'],
                          user_info['type'],
                          user_info['active'],
                          user_info.get('lang', None),
                          temp=True)
        else:
            logger.debug('give up modify, %s', kwargs)

        self.write(json.dumps(kwargs))
        self.finish()

        # now update all information
        if kwargs['error'] == 0:
            for func in all_callbacks:
                try:
                    func()
                except BaseException as e:
                    error = get_exc_plus()
                    logger.critical(error)
                    Message().send(
                        None,
                        None,
                        ('<div class="am-alert am-alert-warning" data-am-alert>'
                         '<pre><code>%s</code></pre>'
                         '</div>') % error
                    )
            user.save()

    def save_pwd(self, user):
        user_info = user.get()
        verify = user_info['verify']
        raw_pwd = self.get_argument('pwd')
        old_pwd = user_info['pwd']
        if old_pwd and user.verify(raw_pwd):
            return 0, ()

        assert len(raw_pwd) >= self.PWD_MIN_LEN
        pwd = sha256_crypt.encrypt(raw_pwd)
        user_info = user.get()
        user_info['pwd'] = pwd
        logger.info('%s changed the pwd', user_info['user'])

        def unmask():
            verify['for'] &= (~User.CHANGEPWD)

        return 0, (unmask,)

    def save_user(self, user):
        user_info = user.get()
        verify = user_info['verify']
        olduser = user_info['user']
        newuser = self.get_argument('user')

        if olduser == newuser:
            return 0, ()

        if not User(newuser).new:
            return self.ERROR_USER_EXISTS, ()

        user_info['user'] = newuser
        # rename folder
        def move_folder():
            oldpath = self.get_user_path(olduser)
            newpath = self.get_user_path(newuser)
            if os.path.exists(oldpath):
                os.rename(oldpath, newpath)

        def unmask():
            verify['for'] &= (~User.CHANGEUSER)

        return 0, (lambda: Article.get_collect().update_many(
                           {'author': olduser},
                           {'$set': {'author': newuser}}),
                   lambda: Message.get_collect().update_many(
                           {'from': olduser},
                           {'$set': {'from': newuser}}),
                   lambda: Message.get_collect().update_many(
                           {'to': olduser},
                           {'$set': {'to': newuser}}),
                   unmask,
                   move_folder
                  )

    # @tornado.gen.coroutine
    def save_email(self, user):
        user_info = user.get()
        verify = user_info['verify']
        oldmail = user_info['email']
        newmail = self.get_argument('email')

        if oldmail == newmail:
            return 0, ()

        if not User(newmail).new:
            return self.ERROR_EMAIL_EXISTS, ()

        logger.debug('user %s change email %s -> %s',
                     user_info['user'], user_info['email'], newmail)
        user_info['email'] = newmail
        user_name = user_info['user']
        code = User.generate()

        def set_code():
            user_info['active'] = False
            verify['for'] |= user.NEWUSER
            verify['code'] = code

        def unmask():
            verify['for'] &= (~User.CHANGEEMAIL)

        # send mail
        def sendmail_callback():
            tr = self.locale.translate
            mailman = Email(newmail, self.locale.code)

            try:
                mailman.send(
                    'change_email',
                    user=user_info['user'],
                    code=code,
                    escaped_code=quote(code))
            except BaseException as e:
                logger.error('failed to send mail to %s(%s)', newmail, e)
                Message().send(
                    None,
                    user_name,
                    tr('We failed to send active email to "{email}", '
                       'please visit "secure" panel to try again.').format(
                        email=newmail)
                )
            else:
                Message().send(
                    None,
                    user_name,
                    tr('An active email has been sent to "{email}", '
                       'please visit to active your account.').format(
                        email=newmail)
                )
        return 0, (lambda: Article.get_collect().update_many(
                           {'author': user_name},
                           {'$set': {'email': newmail}}),
                   sendmail_callback,
                   set_code,
                   unmask
                  )
