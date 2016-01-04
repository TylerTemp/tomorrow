import time
import logging
import tornado.web
from .base import BaseHandler
from lib.db import Auth, User
from lib.tool.generate import generate

logger = logging.getLogger('tomorrow.oauth2.get_token')

class GetTokenHandler(BaseHandler):

    def post(self):
        key = self.get_argument('key')
        secret = self.get_argument('secret')
        code = self.get_argument('code')

        auth = Auth(key)

        if not auth:
            raise tornado.web.HTTPError(500, 'App not found')

        if auth.secret != secret:
            raise tornado.web.HTTPError(500, 'Secret not match')

        code_info = auth.get_code(code)
        if code_info is None:
            raise tornado.web.HTTPError(500, 'Code not found')
        if code_info['expire_at'] < time.time():
            raise tornado.web.HTTPError(500, 'Code expired')

        token = generate()
        expire_at = auth.set_token(token, code_info['user'])

        result = {'token': token, 'expire_at': expire_at,
                  'user': code_info['user']}

        logger.debug(result)

        return self.write(result)
