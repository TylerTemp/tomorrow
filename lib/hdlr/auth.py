import tornado.web
import logging
import re
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
sys.path.pop(0)


# todo: ... a lot todo...

class _Handler(BaseHandler):
    email_re_str = '^[\w\d.+-]+@([\w\d.]+\.)+\w{2,}$'
    email_re = re.compile(email_re_str)

class LoginHandler(_Handler):

    def get(self):
        self.xsrf_token
        redirect = self.get_argument('next', None)
        if redirect:
            signin = '/signin/?next=%s' % quote(redirect)
        else:
            signin = '/signin/'
        return self.render(
            'login.html',
            signin=signin,
        )

    # def post(self):
    #     self.check_xsrf_cookie()

class SigninHandler(_Handler):

    def get(self):
        self.xsrf_token
        ssl = (self.request.protocol == 'https')
        redirect = self.get_argument('next', None)
        if redirect:
            login = '/login/?next=%s' % quote(redirect)
        else:
            login = '/login/'

        return self.render(
            'signin.html',
            login=login,
            ssl=ssl,
            email_re=self.email_re_str,
        )

    # def post(self):
    #     self.check_xsrf_cookie()
