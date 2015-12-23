import logging
from weibo import APIClient

from .base import BaseHandler

logger = logging.getLogger('tomorrow.utiltiy.sina.callback')


class CallbackHandler(BaseHandler):

    def get(self):
        code = self.get_argument('code')
        key, secret = self.get_app()
        client = APIClient(app_key=key, app_secret=secret,
                           redirect_uri=self.callback_url)

        r = client.request_access_token(code)

        access_token = r.access_token
        expires_in = r.expires_in
        self.set_auth(access_token, expires_in)
        return self.redirect('/utility/sina/exec/')
