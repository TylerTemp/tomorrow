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
sys.path.pop(0)

logger = logging.getLogger('auth')

# todo: 1. email verify
#       2. find back password
#       3. work without js


class _Handler(BaseHandler):
    EMAIL_RE_STR = r'^[\w\d.+-]+@([\w\d.]+\.)+\w{2,}$'
    EMAIL_RE = re.compile(EMAIL_RE_STR)
    USER_RE_STR = r'^[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]{1,100}$'
    USER_RE = re.compile(USER_RE_STR)
    USER_MAX_LEN = 100

    USER_EMPTY = 1
    USER_TOO_LONG = int('10', 2)
    USER_FORMAT = int('100', 2)
    EMAIL_EMPTY = int('1000', 2)
    EMAIL_FORMAT = int('10000', 2)
    PWD_EMPTY = int('100000', 2)
    USER_EXISTS = int('1000000', 2)
    USER_NOT_EXISTS = int('1000000', 2)
    EMAIL_EXISTS = int('10000000', 2)
    EMAIL_NOT_EXISTS = int('10000000', 2)
    PWD_WRONG = int('100000000', 2)

    def render(self, template_name, **kwargs):
        if 'ssl' not in kwargs:
            kwargs['ssl'] = (self.request.protocol == 'https')
        return super(BaseHandler, self).render(template_name, **kwargs)


class LoginHandler(_Handler):

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
            signin=signin,
        )

    def post(self):
        self.check_xsrf_cookie()
        redirect = self.get_argument('next', None)

        flag = 0

        user_or_email = self.get_argument('user')
        pwd = self.get_argument('pwd')
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
                temp = (not self.get_argument('remember', False))
                self.set_user(user.user, user.user_info['type'], temp=temp)

        result = {'error': flag}

        if not self.is_ajax():
            if flag == 0:
                redirect = redirect or '/'
            else:
                if redirect:
                    result['next'] = redirect
                redirect = ''.join((self.request.uri, '?', urlencode(result)))
            return self.redirect(redirect)

        result['redirect'] = (
            self.safe_redirect(redirect) if redirect is not None else '/')
        return self.write(json.dumps(result))


class SigninHandler(_Handler):

    def get(self):
        self.xsrf_token
        redirect = self.get_argument('next', None)
        if redirect:
            login = '/login/?' + urlencode({'next': redirect})
        else:
            login = '/login/'

        return super(SigninHandler, self).render(
            'signin.html',
            login=login,
        )

    def post(self):
        self.check_xsrf_cookie()
        user = self.get_argument('user')
        email = self.get_argument('email')
        pwd = self.get_argument('pwd')
        redirect = self.get_argument('next', None)
        flag = 0

        if not user:
            flag |= self.USER_EMPTY
        if not email:
            flag |= self.EMAIL_EMPTY
        elif self.EMAIL_RE.match(email) is None:
            flag |= self.EMAIL_WRONG
        if not pwd:
            flag |= self.PWD_EMPTY

        # todo verify email
        if flag == 0:
            user = User(user)
            if not user.new:
                flag |= self.USER_EXISTS
            email_or_none = User.find_user(email)
            if email_or_none is not None:
                flag |= self.EMAIL_EXISTS

            if flag == 0:
                user.add(email=email, pwd=pwd)
                self.set_user(user=user.user,
                              type=user.user_info['type'],
                              temp=True)

        result = {'error': flag}

        if not self.is_ajax():
            # ok
            if flag == 0:
                return self.redirect(
                    self.safe_redirect(redirect)
                        if redirect is not None
                    else '/hi/%s/' % quote(user.user))

            if redirect is not None:
                result['next'] = redirect
            redirect = ''.join((self.request.uri, '?', urlencode(result)))
            return self.redirect(redirect)

        result['redirect'] = redirect or '/'
        return self.write(json.dumps(result))


class LogoutHandler(_Handler):

    def get(self):
        self.logout()
        return self.flush()

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
    }
    for k, v in dic.items():
        print('var %s = %s;' % (k, v))
