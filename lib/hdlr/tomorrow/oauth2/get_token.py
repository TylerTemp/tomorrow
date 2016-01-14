import time
import logging
import tornado.web
import tornado.ioloop
from .base import BaseHandler
from lib.db.tomorrow import Auth, User
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

        token = auth.generate_token()
        expire_at = auth.set_token(token, code_info['uid'])
        self.do_at(lambda: auth.clear_token(token), expire_at)

        user = User.by_id(code_info['uid'])

        result = {'token': token, 'expire_at': expire_at,
                  'uid': str(user._id), 'name': str(user)}

        logger.debug(result)

        return self.write(result)