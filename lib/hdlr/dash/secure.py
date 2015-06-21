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
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.db import User
from lib.config import Config
from lib.tool.generate import generate
from lib.tool.mail import Email
from lib.hdlr.dash.base import ItsMyself
from lib.hdlr.dash.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.secure')


class SecureHandler(BaseHandler):

    ERROR_NOT_VERIFY_EMAIL = 1
    ERROR_FAILED_SEND_EMAIL = 2
    ERROR_NOTHING_TO_SEND = 3

    @tornado.web.authenticated
    @ItsMyself('secure/')
    def get(self, user):

        self.xsrf_token

        user = User(self.current_user['user'])
        user_info = user.get()
        verify_mail = ('verify' in user_info and
                       user_info['verify']['for'] == user.NEWEMAIL)

        return self.render(
            'dash/secure.html',
            verify_mail=verify_mail,
            user_email=user_info['email'],
            active=user_info['active'],
            act="secure",
        )

    @tornado.web.authenticated
    @ItsMyself('secure/')
    @tornado.web.asynchronous
    @tornado.gen.engine
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
                logger.debug('user %s need verify email before %s',
                             user_info['user'], action)
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

        logger.info('user: %s; email: %s; for: %s, expire: %s, code: %s',
                    user_info['user'], email, action, expire, code)

        user.set_code(for_=for_, code=code, expire=expire)
        user.save()

        mail_man = Email(self.locale.code)
        args = {'email': email, 'user': user_info['user'], 'code': code}
        if for_ == user.NEWEMAIL:
            args['url'] = '/am/%s/verify/newmail/%s/' % (
                quote(user_info['user']),
                quote(code))
            func = mail_man.verify_new_mail
        elif for_ == user.CHANGEEMAIL:
            args['expire'] = expire
            args['url'] = '/am/%s/verify/changemail/%s/' % (
                quote(user_info['user']),
                quote(code))
            func = mail_man.verify_change_mail
        elif for_ == user.CHANGEUSER:
            args['expire'] = expire
            args['url'] = '/am/%s/verify/changeuser/%s/' % (
                quote(user_info['user']),
                quote(code))
            func = mail_man.verify_change_user
        elif for_ == user.CHANGEPWD:
            args['expire'] = expire
            args['url'] = '/am/%s/verify/changepwd/%s/' % (
                quote(user_info['user']),
                quote(code))
            func = mail_man.verify_change_pwd

        sent = yield func(**args)
        if not sent:
            flag = self.ERROR_FAILED_SEND_EMAIL

        self.write(json.dumps({'error': flag, 'email': email}))
        self.finish()
        return
