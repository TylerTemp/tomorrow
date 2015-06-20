import tornado.web
import logging
import re
import json
try:
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    from urllib import quote
    from urllib import urlencode

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import User
from lib.tool.mail import Email
from lib.tool.generate import generate
from lib.hdlr.base import EnsureSsl
sys.path.pop(0)

logger = logging.getLogger('tomorrow.auth')

# todo: 1. email verify
#       2. find back password
#       3. work without js


class _Handler(BaseHandler):
    EMAIL_RE_STR = r'^[\w\d.+-]+@([\w\d.]+\.)+\w{2,}$'
    EMAIL_RE = re.compile(EMAIL_RE_STR)
    USER_RE_STR = r'^[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]{1,100}$'
    USER_RE = re.compile(USER_RE_STR)
    USER_MAX_LEN = 100

    USER_EMPTY = 1  # login/signin
    USER_TOO_LONG = int('10', 2)  # signin
    USER_FORMAT = int('100', 2)  # signin
    EMAIL_EMPTY = int('1000', 2)  # signin
    EMAIL_FORMAT = int('10000', 2)  # signin
    PWD_EMPTY = int('100000', 2)  # login/signin
    USER_EXISTS = int('1000000', 2)  # signin
    USER_NOT_EXISTS = int('1000000', 2)  # login
    EMAIL_EXISTS = int('10000000', 2)  # signin
    EMAIL_NOT_EXISTS = int('10000000', 2)  # login
    PWD_WRONG = int('100000000', 2)  # login
    SEND_EMAIL_FAILED = int('100000000', 2)  # signin

    def render(self, template_name, **kwargs):
        if 'ssl' not in kwargs:
            kwargs['ssl'] = (self.request.protocol == 'https')
        return super(BaseHandler, self).render(template_name, **kwargs)


class LoginHandler(_Handler):

    @EnsureSsl(permanent=True)
    def get(self):
        redirect = self.get_argument('next', None)

        if self.get_current_user():
            return self.redirect(
                self.safe_redirect(redirect) if redirect is not None else '/')

        self.xsrf_token
        if redirect:
            signin = '/signin/?' + urlencode(
                {'next': self.safe_redirect(redirect)})
        else:
            signin = '/signin/'

        return super(LoginHandler, self).render(
            'login.html',
            signin=self.get_ssl(signin),
        )

    @EnsureSsl(permanent=True)
    def post(self):
        self.check_xsrf_cookie()

        flag = 0

        user_or_email = self.get_argument('user')
        pwd = self.get_argument('pwd')
        redirect = self.get_argument('next', None)

        if not user_or_email:
            flag |= self.USER_EMPTY
        if not pwd:
            flag |= self.PWD_EMPTY

        if flag == 0:
            user = User(user_or_email)
            if user.new:
                flag |= (self.EMAIL_NOT_EXISTS
                         if '@' in user_or_email
                         else self.USER_NOT_EXISTS)

            elif not user.verify(pwd):
                flag |= self.PWD_WRONG

            else:
                user_info = user.get()
                user = user_info['user']
                email = user_info['email']
                type = user_info['type']
                temp = (not self.get_argument('remember', False))
                self.set_user(user, email, type, user_info['active'],
                              user_info.get('lang', None), temp=temp)

        result = {'error': flag}

        if not self.is_ajax():
            if flag == 0:
                redirect = self.get_non_ssl(redirect or '/')
            else:
                if redirect:
                    result['next'] = redirect
                redirect = ''.join((self.request.uri, '?', urlencode(result)))
            return self.redirect(redirect)

        redirect = self.safe_redirect(redirect) if redirect is not None else '/'
        if flag == 0:
            redirect = self.get_non_ssl(redirect)
        result['redirect'] = redirect
        return self.write(json.dumps(result))


class SigninHandler(_Handler):

    @EnsureSsl(permanent=True)
    def get(self):
        self.xsrf_token
        redirect = self.get_argument('next', None)
        if redirect:
            login = '/login/?' + urlencode({'next': redirect})
        else:
            login = '/login/'

        return super(SigninHandler, self).render(
            'signin.html',
            login=self.get_ssl(login),
        )

    @EnsureSsl(permanent=True)
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        self.check_xsrf_cookie()

        user = self.get_argument('user')
        email = self.get_argument('email')
        pwd = self.get_argument('pwd')
        redirect = '/am/%s/' % quote(user)
        flag = 0

        if not user:
            flag |= self.USER_EMPTY
        if not email:
            flag |= self.EMAIL_EMPTY
        elif self.EMAIL_RE.match(email) is None:
            flag |= self.EMAIL_WRONG
        if not pwd:
            flag |= self.PWD_EMPTY

        if flag == 0:

            user = User(user)
            if not user.new:
                flag |= self.USER_EXISTS

            email_or_none = User.find_user(email)
            if email_or_none is not None:
                flag |= self.EMAIL_EXISTS

            if flag == 0:

                user.add(email=email, pwd=pwd)

                secret = generate()
                user.set_code(for_=user.NEWEMAIL, code=secret)
                user.save()

                user_info = user.get()
                self.set_user(user=user_info['user'],
                              email=user_info['email'],
                              type=user_info['type'],
                              active=user_info['active'],
                              lang=user_info.get('lang', 'zh_CN'),
                              temp=True)

                mailman = Email(self.locale.code)
                url = '/am/%s/verify/newmail/%s/' % (quote(user_info['user']),
                                                     quote(secret))
                sended = yield mailman.verify_new_mail(
                    email, user_info['user'], secret, url)
                if not sended:
                    logger.error('failed to send main to %s', user_info['user'])
                    flag |= self.SEND_EMAIL_FAILED

        result = {'error': flag}

        if not self.is_ajax():
            # ok
            if flag == 0 or flag & self.SEND_EMAIL_FAILED:
                self.redirect(redirect)
                self.finish()
                return

            redirect = ''.join((self.request.uri, '?', urlencode(result)))
            self.redirect(redirect)
            self.finish()
            return

        result['redirect'] = redirect
        self.write(json.dumps(result))
        self.finish()
        return

class LogoutHandler(_Handler):

    def get(self):
        self.logout()
        return self.redirect('/')

    post = get

if __name__ == '__main__':
    print('copy following string to `static/js/app.js`\n')
    dic = {
        'EMAIL_RE': '/%s/' % _Handler.EMAIL_RE_STR,
        'USER_RE': '/%s/' % _Handler.USER_RE_STR,
        'USER_MAX_LEN': _Handler.USER_MAX_LEN,



        'MASK_USER_EMPTY': _Handler.USER_EMPTY,
        'MASK_USER_TOO_LONG': _Handler.USER_TOO_LONG,
        'MASK_USER_FORMAT_WRONG': _Handler.USER_FORMAT,
        'MASK_USER_EXISTS': _Handler.USER_EXISTS,
        'MASK_USER_NOT_EXISTS': _Handler.USER_NOT_EXISTS,
        'MASK_EMAIL_EMPTY': _Handler.EMAIL_EMPTY,
        'MASK_EMAIL_FORMAT_WRONG': _Handler.EMAIL_FORMAT,
        'MASK_EMAIL_EXISTS': _Handler.EMAIL_EXISTS,
        'MASK_EMAIL_NOT_EXISTS': _Handler.EMAIL_NOT_EXISTS,
        'MASK_PWD_EMPTY': _Handler.PWD_EMPTY,
        'MASK_PWD_WRONG': _Handler.PWD_WRONG,
        'MAST_SEND_EMAIL_FAILED': _Handler.SEND_EMAIL_FAILED,
    }
    for k, v in dic.items():
        print('var %s = %s;' % (k, v))
