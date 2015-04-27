import tornado.web
import logging
import json
import time
import base64
import binascii
try:
    from urllib.parse import urljoin
    from urllib.parse import quote
except ImportError:
    from urlparse import urljoin
    from urlparse import quote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import User
from lib.config import Config
from lib.tool.minsix import open
sys.path.pop(0)

cfg = Config()
logger = logging.getLogger('tomorrow.upload')


class UploadHandler(BaseHandler):
    NO_PERMISSION = 1
    SIZE_TOO_BIG = 2
    DUPLICATED_NAME = 4
    DECODE_ERROR = 8

    @tornado.web.authenticated
    def post(self, user, to):
        # todo: block the non-allowed account
        self.check_xsrf_cookie()

        flag = 0

        userinfo = self.get_current_user()
        user = userinfo['user']
        type = userinfo['type']

        if type < User.admin:
            return self.write(json.dumps({'error': self.NO_PERMISSION}))

        urldata = self.get_argument('urldata')
        filename = self.get_argument('name')
        folder = os.path.join(self.get_user_path(user), to)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        mainurl = self.get_user_url(user)

        if os.path.exists(os.path.join(folder, filename)):
            ext = os.path.splitext(filename)[-1]
            mainname = time.strftime('%y-%m-%d-%H-%M-%S',
                                     time.localtime(time.time()))
            filename = mainname + ext

            if os.path.exists(os.path.join(folder, filename)):
                return self.write(json.dumps({'error': self.DUPLICATED_NAME}))

        _, data64 = urldata.split(',', 1)
        try:
            bindata = base64.b64decode(data64)
        except binascii.Error:
            return self.write(json.dumps({'error': self.DECODE_ERROR}))

        with open(os.path.join(folder, filename), 'wb') as f:
            f.write(bindata)

        return self.write(json.dumps({
            'error': 0,
            'name': filename,
            'url': urljoin(mainurl, '%s/%s' % (to, filename))
        }))
