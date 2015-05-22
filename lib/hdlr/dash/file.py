import tornado.web
import logging
import json
import time
import base64
import binascii
import mimetypes
try:
    from urllib.parse import unquote
    from urllib.parse import quote
    from urllib.parse import urljoin
except ImportError:
    from urllib import unquote
    from urllib import quote
    from urlparse import urljoin

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.db import User
from lib.config import Config
from lib.tool.minsix import open
from lib.tool.unitsatisfy import unit_satisfy
from lib.hdlr.dash.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.file')


class FileHandler(BaseHandler):
    config = Config()

    NO_PERMISSION = 1
    SIZE_TOO_BIG = 2
    DUPLICATED_NAME = 4
    DECODE_ERROR = 8

    NOT_FOUND = 1
    DELETE_FAILED = 2

    type2icon = {
        'text': 'am-icon-file-text-o',
        'word': 'am-icon-file-word-o',
        'zip': 'am-icon-file-archive-o',
        'audio': 'am-icon-file-audio-o',
        'excel': 'am-icon-file-excel-o',
        'image': 'am-icon-file-image-o',
        'video': 'am-icon-file-video-o',
        'unknown': 'am-icon-file-o',
        'pdf': 'am-icon-file-pdf-o',
        'ppt': 'am-icon-file-powerpoint-o'
    }

    def _is_myself(self, user):
        url_user_name = unquote(user)
        current_user = self.current_user
        user_name = current_user['user']
        user_type = current_user['type']
        logger.debug('user=%s, urluser=%s', user_name, url_user_name)
        return (user_name == url_user_name or user_type < User.root)

    def assert_get_myself(func):

        def wrapper(self, user, to):
            if not self._is_myself(user):
                self.set_status(403)
                self.write(
                    '''<!doctype html>
                    <html>
                      <head>
                        <meta charset="utf-8">
                        <title>{title}</title>
                      </head>
                      <body>
                        {body}
                      </body>
                    </html>'''.format(
                        title=self.locale.translate('Permission Denied'),
                        body=self.locale.translate(
                            "Sorry, you're not allow to see others' "
                            "uploaded files"),
                    )
                )
                self.finish()
                return
            return func(self, user, to)

        return wrapper

    def assert_post_myself(func):

        def wrapper(self, user, to):
            if not self._is_myself(user):
                raise tornado.web.HTTPError(
                    403, "%s is not allowed to upload here", user)
            return func(self, user, to)

        return wrapper

    @tornado.web.authenticated
    @assert_get_myself
    def get(self, user, to):
        self.xsrf_token
        user_info = self.current_user
        user_name = user_info['user']
        folder = os.path.join(self.get_user_path(user_name), to)
        url = ''.join((self.get_user_url(user_name), to, '/%s'))
        size_limit = self.config.size_limit[user_info['type']]
        return self.render(
            'dash/image.html' if to == 'img' else 'dash/file.html',
            size_limit=size_limit,
            files=self.file_attrs(folder, url) if os.path.isdir(folder) else (),
            act=to
        )

    def file_attrs(self, path, url_template):
        dirpath, dirnames, filenames = next(os.walk(path))
        for file_name in filenames:
            icon = self.icon(file_name)
            size = os.path.getsize(os.path.join(path, file_name))
            size_str = '%.2f %s' % unit_satisfy(size)
            url = url_template % quote(file_name)
            yield {'name': file_name,
                   'icon': icon,
                   'size': size_str,
                   'url': url
                  }

    def icon(self, filename):
        _, ext = os.path.splitext(filename)
        icons = self.type2icon
        tp = 'unknown'
        if ext in ('.doc', '.docx', '.rtf', '.uof', '.odt', '.fodt', '.uot'):
            tp = 'word'
        elif ext in ('.pps', '.ppsx', '.ppt', '.pptx', '.odp', '.odg', '.uop'):
            tp = 'ppt'
        elif ext in ('.xsl', '.xslx', '.dos', '.uos', '.dbf', '.csv', '.et',
                     '.prn', '.dif'):
            tp = 'excel'
        elif ext in ('.html', '.xml', '.xhtml', '.txt', '.log'):
            tp = 'text'
        elif ext in ('.rar', '.zip', '.tar', '.gz', '.gz2'):
            tp = 'zip'
        else:
            mime_type = mimetypes.guess_type(filename)
            file_mime = mime_type[0]
            if file_mime is not None:
                main, sub = file_mime.split('/')
                if main in ('audio', 'video', 'text', 'image'):
                    tp = main
        return icons[tp]

    @tornado.web.authenticated
    @assert_post_myself
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, user, to):
        self.check_xsrf_cookie()

        userinfo = self.current_user
        user = userinfo['user']
        type = userinfo['type']

        if type < User.admin:
            self.write(json.dumps({'error': self.NO_PERMISSION}))
            self.finish()
            return

        action = self.get_argument('action', 'upload')

        if action == 'upload':
            self.upload(to)
        else:
            self.delete(to)

    def delete(self, to):
        user = self.current_user['user']
        filename = self.get_argument('name')
        path = os.path.join(self.get_user_path(user), to, filename)
        error = 0
        if not os.path.isfile(path):
            error = self.NOT_FOUND
        else:
            try:
                os.remove(path)
            except BaseException as e:
                logger.error(e)
                error = self.DELETE_FAILED
        self.write(json.dumps({'error': error, 'name': filename}))
        self.finish()
        logger.debug('deleted %s', filename)
        return

    @tornado.gen.coroutine
    def upload(self, to):
        user = self.current_user['user']
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
                self.write(json.dumps({'error': self.DUPLICATED_NAME}))
                self.finish()
                return

        bindata = yield self.decode(urldata)
        if bindata is None:
            self.write(json.dumps({'error': self.DECODE_ERROR}))
            self.finish()
            return

        yield self.save_file(os.path.join(folder, filename), bindata)

        self.write(json.dumps({
            'error': 0,
            'name': filename,
            'icon': self.icon(filename),
            'size': len(bindata),
            'url': urljoin(mainurl, '%s/%s' % (to, filename))
        }))
        self.finish()
        logger.info('saved %s', filename)
        return

    @tornado.gen.coroutine
    def decode(self, dataurl):
        _, data64 = dataurl.split(',', 1)
        try:
            bindata = base64.b64decode(data64)
        except binascii.Error as e:
            logger.error(e)
            bindata = None
        raise tornado.gen.Return(value=bindata)

    @tornado.gen.coroutine
    def save_file(self, path, data):
        with open(path, 'wb') as f:
            f.write(data)
        raise tornado.gen.Return()
