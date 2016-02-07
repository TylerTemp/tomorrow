from .base import BaseHandler
import logging
import json
try:
    from urllib.parse import urlencode
except ImportError:
    from urlparse import urlencode


class LoginHandler(BaseHandler):
    logger = logging.getLogger('jolla.login')

    def get(self):
        return self.render(
            'jolla/login.html',
            tomorrow_url=self.get_tomorrow_url(),
        )

    def get_tomorrow_url(self):
        app = self.config.tomorrow
        main = app['auth_url']
        return '%s?%s' % (
            main, urlencode({'key': app['key'], 'callback': app['callback']}))


class LogoutHandler(BaseHandler):

    def get(self):
        self.logout()
        return self.redirect('/')

    def post(self):
        self.logout()
        return self.write(json.dumps({'error': 0}))
