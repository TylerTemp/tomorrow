import tornado.web
import tornado.gen
import logging
import re
import json
try:
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    from urllib import quote
    from urllib import urlencode

from .base import BaseHandler
from lib.db.tomorrow import User
from lib.hdlr.base import EnsureSsl

logger = logging.getLogger('tomorrow.blog.auth')


class _Handler(BaseHandler):
    EMAIL_RE_STR = r'^[\w\d.+-]+@([\w\d.]+\.)+\w{2,}$'
    EMAIL_RE = re.compile(EMAIL_RE_STR)
    USER_RE_STR = (r'^[a-zA-Z0-9\u4e00-\u9fa5_\ \-][a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]'
                   r'|[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-][a-zA-Z0-9\u4e00-\u9fa5_\ \-]'
                   r'|[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]{3,100}$')
    USER_RE = re.compile(USER_RE_STR)
    USER_MAX_LEN = 100
    USER_MIN_LEN = 2

    USER_TOO_SHORT = 1  # login/signin
    USER_TOO_LONG = int('10', 2)  # signin
    USER_FORMAT = int('100', 2)  # signin
    EMAIL_EMPTY = int('1000', 2)  # signin
    EMAIL_FORMAT = int('10000', 2)  # signin
    PWD_TOO_SHORT = int('100000', 2)  # login/signin
    USER_EXISTS = int('1000000', 2)  # signin
    USER_NOT_EXISTS = int('1000000', 2)  # login
    EMAIL_EXISTS = int('10000000', 2)  # signin
    EMAIL_NOT_EXISTS = int('10000000', 2)  # login
    PWD_WRONG = int('1000000000', 2)  # login
    SEND_EMAIL_FAILED = int('100000000', 2)  # signin
    PWD_MIN_LENGTH = 8

    def login(self, user, temp=False):
        if temp:
            kwd = {'expires_days': None}
        else:
            kwd = {}
        self.set_secure_cookie('user', str(user._id), **kwd)


class LoginHandler(_Handler):

    @EnsureSsl(permanent=True)
    def get(self):
        redirect = self.get_argument('next', None)

        if self.current_user is not None:
            return self.redirect(redirect or '/')

        self.xsrf_token
        if redirect:
            signin = '/signin/?' + urlencode(
                {'next': redirect})
        else:
            signin = '/signin/'

        return super(LoginHandler, self).render(
            'tomorrow/blog/login.html',
            signin=signin,
        )

    @EnsureSsl(permanent=True)
    def post(self):
        self.check_xsrf_cookie()

        flag = 0

        user_or_email = self.get_argument('user')
        pwd = self.get_argument('pwd')
        redirect = self.get_argument('next', None)

        if len(user_or_email) < 2:
            flag |= self.USER_TOO_SHORT

        if flag == 0:
            user = User(user_or_email)
            if not user:
                flag |= (self.EMAIL_NOT_EXISTS
                         if '@' in user_or_email
                         else self.USER_NOT_EXISTS)

            elif not user.check_pwd(pwd):
                flag |= self.PWD_WRONG

            else:
                self.login(user)

        result = {'error': flag}

        if not self.is_ajax():
            if flag == 0:
                redirect = self.get_non_ssl(redirect or '/')
            else:
                if redirect:
                    result['next'] = redirect
                redirect = ''.join((self.request.uri, '?', urlencode(result)))
            return self.redirect(redirect)

        redirect = redirect or '/'
        result['redirect'] = redirect
        logger.debug(result)
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
            'tomorrow/blog/signin.html',
            login=login,
        )

    @EnsureSsl(permanent=True)
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        self.check_xsrf_cookie()

        name = self.get_argument('user')
        email = self.get_argument('email')
        pwd = self.get_argument('pwd')
        redirect = '/am/%s/' % quote(name)
        flag = 0

        if len(name) < 2:
            flag |= self.USER_TOO_SHORT
        elif len(name) > self.USER_MAX_LEN:
            flag |= self.USER_TOO_LONG
        elif self.USER_RE.match(name) is None:
            flag |= self.USER_FORMAT
        if not email:
            flag |= self.EMAIL_EMPTY
        elif self.EMAIL_RE.match(email) is None:
            flag |= self.EMAIL_FORMAT
        if len(pwd) < self.PWD_MIN_LENGTH:
            flag |= self.PWD_TOO_SHORT

        if flag == 0:

            user = User(name)
            if user:
                flag |= self.USER_EXISTS

            user = User(email)
            if user:
                flag |= self.EMAIL_EXISTS

            if flag == 0:

                user.name = name
                user.email = email
                user.pwd = pwd
                code = user.generate()
                user.set_code(for_=user.NEWUSER, code=code)
                user.save()

                self.login(user, temp=True)

        result = {'error': flag}

        if self.is_ajax():
            result['redirect'] = redirect
            self.write(json.dumps(result))
            self.finish()
        else:
            # ok
            if flag == 0:
                self.redirect(redirect)
                self.finish()
            else:
                redirect = '%s?%s' % (self.request.uri, urlencode(result))
                self.redirect(redirect)
                self.finish()


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
        'USER_MIN_LEN': _Handler.USER_MIN_LEN,

        'MASK_USER_TOO_SHORT': _Handler.USER_TOO_SHORT,
        'MASK_USER_TOO_LONG': _Handler.USER_TOO_LONG,
        'MASK_USER_FORMAT_WRONG': _Handler.USER_FORMAT,
        'MASK_USER_EXISTS': _Handler.USER_EXISTS,
        'MASK_USER_NOT_EXISTS': _Handler.USER_NOT_EXISTS,
        'MASK_EMAIL_EMPTY': _Handler.EMAIL_EMPTY,
        'MASK_EMAIL_FORMAT_WRONG': _Handler.EMAIL_FORMAT,
        'MASK_EMAIL_EXISTS': _Handler.EMAIL_EXISTS,
        'MASK_EMAIL_NOT_EXISTS': _Handler.EMAIL_NOT_EXISTS,
        'MASK_PWD_TOO_SHORT': _Handler.PWD_TOO_SHORT,
        'MASK_PWD_WRONG': _Handler.PWD_WRONG,
        'MAST_SEND_EMAIL_FAILED': _Handler.SEND_EMAIL_FAILED,

        'PWD_MIN_LENGTH': _Handler.PWD_MIN_LENGTH
    }
    for k, v in dic.items():
        print('var %s = %s;' % (k, v))
