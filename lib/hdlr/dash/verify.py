import tornado.web
import logging
import json
import re
import time
from passlib.hash import sha256_crypt
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.db import User
from lib.db import Article
from lib.config import Config
from lib.tool.generate import generate
from lib.tool.mail import Email
from lib.tool.ensure import EnsureSsl
from lib.hdlr.dash.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.verify')


class VerifyHandler(BaseHandler):
    ERROR_EXPIRED = 1
    ERROR_NOT_CHANGE = 2
    ERROR_NOT_SEND = 4
    ERROR_EXISTS = 8
    ERROR_FORMAT = 16
    USER_RE = re.compile(r'^[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]{1,100}$')
    act2code = {
        'newuser': User.NEWEMAIL,
        'newmail': User.NEWEMAIL,
        'changemail': User.CHANGEEMAIL,
        'changeuser': User.CHANGEUSER,
        'changepwd': User.CHANGEPWD,
    }

    @EnsureSsl(True)
    def get(self, user, act, code):
        if act == 'changepwd' and not self.is_ssl():
            return self.redirect(self.get_ssl())
        code = unquote(code)
        urluser = unquote(user)
        main_url = self.get_non_ssl('/am/%s' % urluser)
        user = User(urluser)
        subtitle = {
            'newuser': 'setup new user',
            'newmail': 'setup new user',
            'changemail': 'change your email',
            'changeuser': 'change your user',
            'changepwd': 'change your password',
        }[act]
        expected = self.act2code[act]
        kwargs = {'main_url': main_url,
                  'subtitle': subtitle,
                  'user_name': urluser,
                  'user_type': user.normal,
                  'error': None}
        if user.new:
            logger.debug('user %s not found', urluser)
            kwargs['error'] = 'nouser'
            return self.render(
                'dash/verify.html',
                **kwargs
            )

        user_info = user.get()
        kwargs['user_name'] = user_info['user']
        kwargs['user_type'] = user_info['type']
        kwargs['user_pwd'] = user_info['pwd']
        kwargs['user_email'] = user_info['email']
        if user_info['user'] is not None:
            kwargs['main_url'] = '/am/%s' % quote(user_info['user'])
        else:
            kwargs['main_url'] = '/am/%s' % quote(user_info['email'])
        if 'verify' not in user_info:
            kwargs['error'] = 'noapply'
            logger.debug('no apply')
            return self.render(
                'dash/verify.html',
                **kwargs
            )
        elif user_info['verify']['for'] != expected:
            kwargs['error'] = 'notapply'
            logger.debug('not apply')
            return self.render(
                'dash/verify.html',
                **kwargs
            )
        # don't change the comparing order!
        elif time.time() > user_info['verify'].get('expire', time.time()):
            kwargs['error'] = 'expire'
            logger.debug('expire')
            return self.render(
                'dash/verify.html',
                **kwargs
            )
        elif user_info['verify']['code'] != code:
            kwargs['error'] = 'wrongcode'
            logger.debug('wrongcode')
            return self.render(
                'dash/verify.html',
                **kwargs
            )

        if expected == User.NEWEMAIL:
            kwargs.update(self.new_user(user))
        elif expected == User.CHANGEEMAIL:
            kwargs['for_'] = 'email'
        elif expected == User.CHANGEPWD:
            kwargs['for_'] = 'pwd'
        elif expected == User.CHANGEUSER:
            kwargs['for_'] = 'user'

        logger.debug(kwargs)

        return self.render(
            'dash/verify.html',
            **kwargs
        )

    def new_user(self, user):
        user_info = user.get()
        verify_info = user_info['verify']

        if user_info['user'] is not None:
            user_info.pop('verify')
            user_info['active'] = True
            user.save()
            self.set_user(user_info['user'], user_info['email'],
                          user_info['type'], user_info['active'], temp=True)
            return {'error': 'succeed'}

        return {'for_': None}

    @EnsureSsl(True)
    @tornado.web.asynchronous
    # @tornado.gen.coroutine
    def post(self, user, act, code):
        # validated by get, so raise when unexpected
        user = User(unquote(user))
        assert not user.new
        verify = user.get()['verify']
        expected = self.act2code[unquote(act)]
        if verify['for'] != expected:
            raise tornado.web.HTTPError(500, 'user request for %s, not %s',
                                        expected, act)

        # this should not raise
        if 'expire' in verify and verify['expire'] < time.time():
            logger.debug('expired: %s', user)
            self.write(json.dumps({'error': self.ERROR_EXPIRED}))
            self.finish()
            return

        if expected == User.NEWEMAIL:
            self.save_new(user)
        elif expected == User.CHANGEEMAIL:
            self.save_email(user)
        elif expected == User.CHANGEPWD:
            self.save_pwd(user)
        elif expected == User.CHANGEUSER:
            self.save_user(user)

    def save_new(self, user):
        user_info = user.get()
        if user_info['user'] is None:
            newname = self.get_argument('user')
            if self.USER_RE.match(newname) is None:
                self.write(json.dumps({'error': self.ERROR_FORMAT,
                                       'for': 'newuser',
                                       'user': user_name}))
                self.finish()
                return
            user_info['user'] = newname
        if user_info['pwd'] is None:
            user_info['pwd'] = sha256_crypt.encrypt(self.get_argument('pwd'))
        user_name = user_info['user']
        self.set_user(user_name, user_info['email'],
                      user_info['type'], user_info['active'], temp=True)
        self.write(json.dumps({'error': 0,
                               'for': 'newuser',
                               'user': user_name,
                               'redirect': self.get_non_ssl(
                                    '/am/%s/' % quote(user_name))}))
        self.finish()
        user_info['active'] = True
        user_info.pop('verify')
        user.save()
        logger.info('new user setup %s', user_info['user'])

    def save_pwd(self, user):
        pwd = sha256_crypt.encrypt(self.get_argument('pwd'))
        user_info = user.get()
        user_info['pwd'] = pwd
        self.set_user(user_info['user'], user_info['email'],
                      user_info['type'], user_info['active'],
                      user_info.get('lang', None),
                      temp=True)
        self.write(json.dumps({'error': 0, 'for': 'pwd'}))
        self.finish()
        user_info.pop('verify')
        user.save()
        logger.info('%s changed the pwd', user_info['user'])

    def save_user(self, user):
        user_info = user.get()
        newuser = self.get_argument('user')
        olduser = user_info['user']
        if olduser == newuser:
            self.write(json.dumps({'error': self.ERROR_NOT_CHANGE,
                                   'for': 'user',
                                   'user': olduser}))
            self.finish()
            return

        if not User(newuser).new:
            self.write(json.dumps({'error': self.ERROR_EXISTS,
                                   'for': 'user',
                                   'user': newuser}))
            self.finish()
            return
        # rename folder
        oldpath = self.get_user_path(olduser)
        newpath = self.get_user_path(newuser)
        if os.path.exists(oldpath):
            os.rename(oldpath, newpath)
        # change article owner
        collect = Article.get_collect()
        collect.update_many({'author': olduser}, {'$set': {'author': newuser}})

        self.set_user(newuser, user_info['email'],
                      user_info['type'],
                      user_info['active'],
                      user_info.get('lang', None),
                      temp=True)
        self.write(json.dumps({'error': 0, 'for': 'user',
                               'redirect': self.get_non_ssl(
                                    '/am/%s/' % quote(newuser))}))
        self.finish()
        logger.debug('changed user name %s -> %s', user_info['user'], newuser)
        user_info['user'] = newuser
        user_info.pop('verify')
        user.save()

    @tornado.gen.coroutine
    def save_email(self, user):
        user_info = user.get()
        newmail = self.get_argument('email')
        if user_info['email'] == newmail:
            self.write(json.dumps({'error': self.ERROR_NOT_CHANGE,
                                   'for': 'email',
                                   'email': newmail}))
            self.finish()
            return

        if not User(newmail).new:
            self.write(json.dumps({'error': self.ERROR_EXISTS,
                                   'for': 'email',
                                   'email': newmail}))
            self.finish()
            return

        logger.debug('user %s change email %s -> %s',
                     user_info['user'], user_info['email'], newmail)
        user_info['email'] = newmail
        user_name = user_info['user']
        code = generate()
        user_info['active'] = False
        user.set_code(for_=user.NEWEMAIL, code=code)

        # send mail
        mailman = Email(self.locale.code)
        result = yield mailman.verify_new_mail(
            newmail, user_name, code,
            '/am/%s/verify/newmail/%s/' % (quote(user_name), quote(code)))

        # change email for article
        collect = Article.get_collect()
        collect.update_many(
            {'author': user_name},
            {'$set': {'email': newmail}})

        self.write(json.dumps({'error': 0 if result else self.ERROR_NOT_SEND,
                               'for': 'email',
                               'email': newmail,
                               'redirect': self.get_non_ssl(
                                    '/am/%s/' % quote(user_name))}))
        self.finish()
        # user_info.pop('verify')
        user.save()
        return
