import logging
from weibo import APIClient, APIError
from pprint import pformat

from .base import BaseHandler, EnsureSsl

logger = logging.getLogger('tomorrow.utiltiy.sina.exec')


class ExecHandler(BaseHandler):

    def initialize(self):
        self.key, self.secret = self.get_app()
        self.token, self.expire = self.get_auth()
        self._client = None

    def get(self):
        if not (self.key and self.token):
            return self.redirect('/utility/sina/?err=not-auth')

        user_info, error = self.get_user_info()
        return self.render(
            'utility/sina/exec.html',
            user_info=user_info,
            error=error,
            pretty=pformat
        )

    @property
    def client(self):
        if self._client is None:
            client = APIClient(app_key=self.key, app_secret=self.secret,
                               redirect_uri=self.callback_url)
            client.set_access_token(self.token, self.expire)
            self._client = client

        return self._client

    def get_user_info(self):
        try:
            result = self.client.account.get_uid.get(access_token=self.token)
        except APIError as e:
            return None, str(e)
        except BaseException as e:
            logger.info(e)
            return None, 'Unknown Error'
        else:
            uid = result['uid']

        try:
            result = self.client.users.show.get(
                    access_token=self.token, uid=uid)
        except APIError as e:
            return None, str(e)
        except BaseException as e:
            logger.info(e)
            return None, 'Unknown Error'
        else:
            return result, None


