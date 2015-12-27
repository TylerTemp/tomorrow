import logging
import json
import base64
from pprint import pformat
from weibo import Client
import sys
try:
    from io import BytesIO
except ImportError:
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO

py3 = sys.version_info[0] >= 3

from .base import BaseHandler, get_exc_plus

logger = logging.getLogger('tomorrow.utiltiy.sina.exec')


class ExecHandler(BaseHandler):

    def initialize(self):
        self.key, self.secret = self.get_app()
        self.token = self.get_auth()
        self.access_token = self.token['access_token'] if self.token else None
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
            client = Client(api_key=self.key, api_secret=self.secret,
                            redirect_uri=self.callback_url, token=self.token)
            self._client = client

        return self._client

    def get_user_info(self):
        # return None, 'ERROR'
        try:
            result = self.client.get('account/get_uid',
                                     access_token=self.access_token)
        except BaseException as e:
            logger.info(e)
            return None, str(e)
        else:
            uid = result['uid']

        try:
            result = self.client.get('users/show',
                                     access_token=self.access_token, uid=uid)
        except BaseException as e:
            logger.info(e)
            return None, str(e)
        else:
            return result, None

    def post(self):
        func_name = self.get_argument('func')
        method = self.get_argument('method')
        arguments = self.get_argument('arguments')

        func = self.client.get if method.lower() == 'get' else self.client.post
        args = self.parse_arguments(arguments)

        if self.error is None:
            try:
                result = func(func_name, **args)
            except BaseException as e:
                logger.error(e)
                self.error = str(e)

        if self.error is None:
            j_str = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            self.clear()
            self.set_status(500, self.error)
            j_str = json.dumps({'error': self.error})

        return self.write(j_str)


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
                         name, type_, value)

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
            return BytesIO(bindata)

