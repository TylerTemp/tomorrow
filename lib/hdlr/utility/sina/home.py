import logging
import json
from weibo import Client

from .base import BaseHandler


class HomeHandler(BaseHandler):

    logger = logging.getLogger('tomorrow.utiltiy.sina.home')
    def get(self):
        key, secret = self.get_app()
        error = self.get_argument('err', None)
        return self.render(
            'utility/sina/home.html',
            key=key,
            secret=secret,
            error=error
        )

    def post(self):
        app_key = self.get_argument('app-key')
        app_secret = self.get_argument('app-secret')
        self.set_app(app_key, app_secret)
        client = Client(api_key=app_key, api_secret=app_secret,
                        redirect_uri=self.callback_url)

        return self.write(json.dumps({'url': client.authorize_url}))


