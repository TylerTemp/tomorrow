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

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import User, Message
from lib.tool.mail import Email
from lib.tool.generate import generate
from lib.hdlr.base import EnsureSsl
sys.path.pop(0)

logger = logging.getLogger('tomorrow.auth')


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
            signin=self.get_ssl(signin),
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
                              user_info.get('service', None),
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

        redirect = redirect or '/'
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
            'tomorrow/blog/signin.html',
            login=self.get_ssl(login),
        )

    @EnsureSsl(permanent=True)
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        self.check_xsrf_cookie()

        user = self.get_argument('user')
        email = self.get_argument('email')
        pwd = self.get_argument('pwd')
        redirect = '/am/%s/' % quote(user)
        flag = 0

        if len(user) < 2:
            flag |= self.USER_TOO_SHORT
        elif len(user) > USER_MAX_LEN:
            flag |= self.USER_TOO_LONG
        elif self.USER_RE.match(user) is None:
            flag |= self.USER_FORMAT
        if not email:
            flag |= self.EMAIL_EMPTY
        elif self.EMAIL_RE.match(email) is None:
            flag |= self.EMAIL_FORMAT
        if len(pwd) < self.PWD_MIN_LENGTH:
            flag |= self.PWD_TOO_SHORT

        if flag == 0:

            user = User(user)
            if not user.new:
                flag |= self.USER_EXISTS

            email_or_none = User.find_user(email)
            if email_or_none is not None:
                flag |= self.EMAIL_EXISTS

            if flag == 0:

                user.add(email=email, pwd=pwd)
                code = user.generate()
                user.set_code(for_=user.NEWUSER, code=code)
                user.save()

                user_info = user.get()
                user_name = user_info['user']
                self.set_user(user=user_name,
                              email=email,
                              type=user_info['type'],
                              active=user_info['active'],
                              service=user_info.get('service', None),
                              lang=user_info.get('lang', 'zh_CN'),
                              temp=True)

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

        if flag == 0:
            mailman = Email(email, self.locale.code)
            Message().send(
                None,
                user_name,
                self.locale.translate('<h6>Welcome, {user}</h6>'
                '<p>We are sending you a verify email to {email}. '
                'Please check your email to active your account.</p>'
                '<p>You can also refresh this page to see if it has been '
                'sent successfully.</p>').format(user=user, email=email))
            try:
                mailman.send(name='new_user',
                             user=user_name,
                             code=code,
                             escaped_code=quote(secret))
            except BaseException as e:
                logger.error('failed to send active verify to %s',
                             user_info['user'])
                flag |= self.SEND_EMAIL_FAILED
                Message().send(
                    None,
                    user_name,
                    self.locale.translate(
                        'Oops, failed to send the active email. '
                        'Please visit the secure panel to send it again.'
                    ))
            else:
                Message().send(
                    None,
                    user_name,
                    self.locale.translate(
                        'Send email successfully. Please check your email '
                        'account {}'
                    ).format(email)
                )


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
