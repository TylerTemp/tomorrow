import tornado.web
import logging
import json
import time
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.config import Config
from lib.db import User
from lib.db import Article
from lib.tool.generate import generate
from lib.tool.mail import Email
sys.path.pop(0)

logger = logging.getLogger('tomorrow.user')


def its_myself(func):

    def wrapper(self, user):
        userinfo = self.get_current_user()
        urluser = unquote(user)
        if userinfo is None or userinfo['user'] != urluser:
            logger.debug('redirect to %s', urluser)
            return self.redirect('/hi/%s/' % quote(urluser))

        return func(self, user)

    return wrapper


class _Handler(BaseHandler):

    def render(self, template_name, **kwargs):
        user_info = self.get_current_user()
        if 'main_url' not in kwargs:
            kwargs['main_url'] = '/am/%s' % quote(user_info['user'])
        if 'user_name' not in kwargs:
            kwargs['user_name'] = user_info['user']

        if 'user_type' not in kwargs:
            kwargs['user_type'] = user_info['type']

        kwargs['NORMAL'] = User.normal
        kwargs['ADMIN'] = User.admin
        kwargs['ROOT'] = User.root

        return super(_Handler, self).render(
            template_name,
            **kwargs
        )


class DashboardHandler(_Handler):

    @its_myself
    @tornado.web.authenticated
    def get(self, user):

        url_user = unquote(user)

        user_info = self.get_current_user()

        user = User(user_info['user'])
        user_info = user.get()
        user_name = user_info['user']

        verify_mail = ('verify' in user_info and
                       user_info['verify']['for'] == user.NEWEMAIL)

        folder_path = self.get_user_path(user_name)
        file_path = os.path.join(folder_path, 'file')
        if os.path.exists(file_path):
            file_num = len(os.listdir(file_path))
        else:
            file_num = 0
        img_path = os.path.join(folder_path, 'img')
        if os.path.exists(img_path):
            img_num = len(os.listdir(img_path))
        else:
            img_num = 0

        return self.render(
            'dash/home.html',
            user_email=user_info['email'],
            showe_mail=user_info['show_email'],
            active=user_info['active'],
            verify_mail=verify_mail,
            user_type=user_info['type'],
            user_img=user_info.get('img', None),

            article_num=Article.num_by(user_name),
            file_num=file_num,
            img_num=img_num,
        )

class InfoHandler(_Handler):
    config = Config()

    @its_myself
    @tornado.web.authenticated
    def get(self, user):

        user = User(self.get_current_user()['user'])
        user_info = user.get()
        size_limit = self.config.size_limit[user_info['type']]
        if size_limit != float('inf'):
            size_limit = '%.2f %s' % self.unit_satisfy(size_limit)

        return self.render(
            'dash/info.html',
            user_img=user_info.get('img', None),
            user_email=user_info['email'],
            show_email=user_info['show_email'],
            size_limit=size_limit,
        )

    @tornado.web.authenticated
    def post(self, user):

        self.check_xsrf_cookie()

        userinfo = self.get_current_user()
        urluser = unquote(user)
        if userinfo is None or userinfo['user'] != urluser:
            raise tornado.web.HTTPError(500, 'user %s try to modefy user %s',
                                        userinfo['user'], urluser)

        # this should be bool. But I get string('true'/'false'). WHY?
        show_email = self.get_argument('show_email')
        # set to None if it's empty string
        user_img = self.get_argument('img_url', None) or None
        if show_email not in (True, False):
            logger.info('get show_email (%r) of type (%s)',
                show_email, type(show_email))
            show_email = {'true': True, 'false': False}[show_email]
        logger.debug('show_email: %r; user_img: %r', show_email, user_img)
        user = User(userinfo['user'])
        user_info = user.get()
        user_info.update({'img': user_img, 'show_email': show_email})
        user.save()

        return self.write(json.dumps({'error': 0}))

    @classmethod
    def unit_satisfy(cls, b):
        appropriate_size = b
        appropriate_unit = 'B'
        units = ('B', 'KB', 'MB', 'GB', 'TB')
        index = 0

        while (appropriate_size >> 10) >= 1024 and index < len(units) - 1:
            appropriate_size >>= 10
            index += 1
        return (appropriate_size / 1024, units[index])


class SecureHandler(_Handler):

    ERROR_NOT_VERIFY_EMAIL = 1
    ERROR_FAILED_SEND_EMAIL = 2
    ERROR_NOTHING_TO_SEND = 3

    @its_myself
    @tornado.web.authenticated
    def get(self, user):

        self.xsrf_token

        user = User(self.get_current_user()['user'])
        user_info = user.get()
        verify_mail = ('verify' in user_info and
                       user_info['verify']['for'] == user.NEWEMAIL)

        return self.render(
            'dash/secure.html',
            verify_mail=verify_mail,
            user_email=user_info['email'],
            active=user_info['active'],
        )

    @tornado.web.asynchronous
    @tornado.gen.engine
    @tornado.web.authenticated
    def post(self, user):

        userinfo = self.get_current_user()
        urluser = unquote(user)
        if userinfo['user'] != urluser:
            raise tornado.web.HTTPError(500, 'user %s try to modefy user %s',
                                        userinfo['user'], urluser)

        action = self.get_argument('action')  # name/email/pwd/resend
        flag = 0
        user = User(userinfo['user'])
        user_info = user.get()
        if action in ('name', 'pwd'):
            if ('verify' in user_info and
                    user_info['verify']['for'] == user.NEWEMAIL):
                self.write(json.dumps({'error': self.ERROR_NOT_VERIFY_EMAIL}))
                self.finish()
                return
            email = user_info['email']
            for_ = {'name': User.CHANGEUSER, 'pwd': User.CHANGEPWD}[action]
            expire = time.time() + 60 * 60 * 24
            code = generate()
        elif action == 'email':
            if ('verify' in user_info and
                    user_info['verify']['for'] == user.NEWEMAIL):
                for_ = user.NEWEMAIL
                expire = None
                email = self.get_argument('email', None)
                if email is None:
                    email = user_info['email']
                else:
                    user_info['email'] = email
                code = user_info['verify']['code']
            else:
                email = user_info['email']
                for_ = user.CHANGEEMAIL
                expire = time.time() + 60 * 60 * 24
                code = generate()
        elif action == 'resend':
            if 'verify' not in user_info:
                self.write(json.dumps({'error': self.ERROR_NOTHING_TO_SEND}))
                self.finish()
                return
            for_ = user_info['verify']['for']
            expire = user_info['verify'].get('expire', None)
            email = user_info['email']
            code = user_info['verify']['code']
        else:
            raise tornado.web.HTTPError(500, 'Unknown action %s', action)

        logger.info('email: %s; for: %s, expire: %s, code: %s',
                    email, action, expire, code)

        user.set_code(for_=for_, code=code, expire=expire)
        user.save()

        mail_man = Email(self.locale.code)
        args = {'email': email, 'user': user_info['user'], 'code': code}
        if for_ == user.NEWEMAIL:
            args['url']='/am/%s/verify/newmail/%s/' % (quote(user_info['user']),
                                                       quote(code))
            func = mail_man.verify_new_mail
        elif for_ == user.CHANGEEMAIL:
            args['expire']=expire
            args['url']='/am/%s/verify/changemail/%s/' % (
                quote(user_info['user']),
                quote(code))
            func = mail_man.verify_change_mail
        elif for_ == user.CHANGEUSER:
            args['expire']=expire
            args['url']='/am/%s/verify/changeuser/%s/' % (
                quote(user_info['user']),
                quote(code))
            func = mail_man.verify_change_user
        elif for_ == user.CHANGEPWD:
            args['expire']=expire
            args['url']='/am/%s/verify/changepwd/%s/' % (
                quote(user_info['user']),
                quote(code))
            func = main_man.verify_change_pwd

        sent = yield func(**args)
        if not sent:
            flag = self.ERROR_FAILED_SEND_EMAIL

        self.write(json.dumps({'error': flag, 'email': email}))
        self.finish()
        return


class VerifyHandler(_Handler):
    act2code = {
        'newuser': User.NEWEMAIL,
        'newmail': User.NEWEMAIL,
        'changemail': User.CHANGEEMAIL,
        'changeuser': User.CHANGEPWD,
        'changepwd': User.CHANGEUSER,
    }

    def get(self, user, act, code):
        code = unquote(code)
        urluser = unquote(user)
        main_url = '/am/%s' % urluser
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
        # don't change the compare order!
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
        elif expected == User.CHANGEEMAL:
            kwargs['for_'] = 'email'
        elif expected == User.CHANGEPWD:
            kwargs['for_'] = 'pwd'
            kwargs['ssl'] = (self.request.protocol == 'https')
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
                          user_info['type'], temp=True)
            return {'error': 'succeed'}

        return {'for_': None, 'ssl': (self.request.protocol == 'https')}

class InformationHandler(_Handler):

    pass

if __name__ == '__main__':
    for each in (1, 1024, 1024 ** 2, 1024 ** 3, 1024 ** 4, 1024 ** 5, 1024 ** 6):
        print(InfoHandler.unit_satisfy(each+990))
