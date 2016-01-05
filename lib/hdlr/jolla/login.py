from .base import BaseHandler
from lib.config import Config
try:
    from urllib.parse import urlencode
except ImportError:
    from urlparse import urlencode

class LoginHandler(BaseHandler):
    _config = Config()
    _info = _config.jolla_app
    url = '%s?%s' % (
        _info['auth_url'],
        urlencode({'callback': _info['callback'], 'key': _info['key']}))

    def get(self):
        return self.render(
            'jolla/login.html',
            tomorrow_url=self.url,
        )