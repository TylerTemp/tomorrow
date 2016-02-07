import logging
from weibo import Client

from .base import BaseHandler


class CallbackHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.utiltiy.sina.callback')

    def get(self):
        code = self.get_argument('code')
        key, secret = self.get_app()
        client = Client(api_key=key, api_secret=secret,
                        redirect_uri=self.callback_url)

        client.set_code(code)

        result = client.token
        self.set_auth(result)
        return self.redirect('/utility/sina/exec/')
