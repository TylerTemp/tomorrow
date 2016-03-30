import logging
import json
try:
    from urllib.parse import urlunsplit
except ImportError:
    from urlparse import urlunsplit

from lib.hdlr.base import BaseHandler
from lib.tool.tracemore import get_exc_plus

logging.getLogger("requests").setLevel(logging.WARNING)


class BaseHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.utiltiy.sina')
    error_template = 'utility/sina/error.html'


    def check_xsrf_cookie(self):
        return True

    def set_app(self, key, secret):
        self.set_secure_cookie('app-key', key, expires_days=None)
        self.set_secure_cookie('app-secret', secret, expires_days=None)

    def get_app(self):
        key = self.get_secure_cookie('app-key')
        if key is None:
            return None, None

        key = key.decode('utf-8')
        secret = self.get_secure_cookie('app-secret').decode('utf-8')
        return (key, secret)

    def set_auth(self, token):
        self.set_secure_cookie('auth', json.dumps(token), expires_days=None)

    def get_auth(self):
        token = self.get_secure_cookie('auth')
        if token is None:
            return None

        return json.loads(token.decode('utf-8'))

    @property
    def callback_url(self):
        request = self.request
        host = request.host
        protocol = request.protocol
        split_result = (protocol, host, '/utility/sina/callback/', '', '')
        return urlunsplit(split_result)
