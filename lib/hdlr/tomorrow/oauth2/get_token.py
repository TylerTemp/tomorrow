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

        token = generate()
        expire_at = auth.set_token(token, code_info['uid'])
        self.clear_token(auth, token, expire_at)

        u = User.init_by_id(code_info['uid'])
        user_info = u.get()
        name = user_info['user']
        uid = user_info['_id']

        result = {'token': token, 'expire_at': expire_at,
                  'uid': str(uid), 'name': name}

        logger.debug(result)

        return self.write(result)

    def clear_token(self, auth, token, expire_at):
        logger.debug('clear at %s', expire_at)
        tornado.ioloop.IOLoop.instance().add_timeout(
            expire_at,
            auth.clear_token,
            token
        )