import logging
import json
from weibo import APIClient

from .base import BaseHandler, EnsureSsl

logger = logging.getLogger('tomorrow.utiltiy.sina.home')

class HomeHandler(BaseHandler):

    @EnsureSsl(permanent=True)
    def get(self):
        key, secret = self.get_app()
        error = self.get_argument('err', None)
        return self.render(
            'utility/sina/home.html',
            key=key,
            secret=secret,
            error=error
        )

    @EnsureSsl(permanent=True)
    def post(self):
        app_key = self.get_argument('app-key')
        app_secret = self.get_argument('app-secret')
        host = self.request.host
        client = APIClient(app_key=app_key, app_secret=app_secret,
                           redirect_uri=''.join(
                               ('https://',
                                host,
                                '/utility/sina/callback/')))

        msg = None
        try:
            url = client.get_authorize_url()
        except BaseException as e:
            msg = str(e)
        else:
            self.set_app(app_key, app_secret)

        if msg is None:
            result = {'url': url}
        else:
            self.clear()
            self.set_status(500)
            result = {'msg': msg}

        return self.write(json.dumps(result))


