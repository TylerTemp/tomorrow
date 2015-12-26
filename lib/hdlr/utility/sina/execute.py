import logging
import json
import base64
from pprint import pformat
from weibo import APIClient, APIError
import sys

py3 = sys.version_info[0] >= 3

from .base import BaseHandler, get_exc_plus

logger = logging.getLogger('tomorrow.utiltiy.sina.exec')


class ExecHandler(BaseHandler):

    def initialize(self):
        self.key, self.secret = self.get_app()
        self.token, self.expire = self.get_auth()
        self._client = None
        self.error = None

    def get(self):
        if not (self.key and self.secret):
            return self.redirect('/utility/sina/?err=not-auth')

        user_info, error = self.get_user_info()
        # user_info = error = 'error'
        return self.render(
            'utility/sina/exec.html',
            user_info=user_info,
            error=error,
            token=self.token,
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

    def post(self):
        func_name = self.get_argument('func')
        method = self.get_argument('method')
        arguments = self.get_argument('arguments')

        func = self.parse_func(func_name, method)
        args = self.parse_arguments(arguments)

        if self.error is None:
            try:
                result = func(**args)
            except BaseException as e:
                logger.error(e)
                self.error = str(e)
                raise

        if self.error is None:
            j_str = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            self.clear()
            self.set_status(500, self.error)
            j_str = json.dumps({'error': self.error})

        return self.write(j_str)

    def parse_func(self, func_name, method):
        current = self.client
        for each in func_name.split('/'):
            logger.debug(each)
            current = getattr(current, each)
        logger.debug(method)
        return getattr(current, method.lower())

    def parse_arguments(self, arguments):
        args = json.loads(arguments)
        result = {}
        for each in args:
            if self.error is not None:
                return result
            name = each['name']
            type_ = each['type']
            value = each['value']
            if type_ == 'int':
                value = int(value)
            elif type_ == 'binary':
                value = self.b64_to_binary(value)

            logger.debug('name: %s; type: %s; value: %s',
                         name, type_,
                         value[:50] if type_ == 'binary' else value)

            result[name] = value

        return result

    def b64_to_binary(self, value):
        _, data64 = value.split(',', 1)

        if not data64:
            self.error = 'binary file format error'
            logger.error(self.error)
            return

        if py3:
            data64 = data64.encode()

        try:
            bindata = base64.b64decode(data64)
        except BaseException as e:
            logger.info(e)
            self.error = 'binary file format error'
        else:
            return bindata

