import tornado.web
import logging
import json
import binascii
import mimetypes
import os
try:
    from urllib.parse import unquote, quote, urljoin, urlsplit
except ImportError:
    from urllib import unquote, quote
    from urlparse import urljoin, urlsplit

from lib.db.tomorrow import User
from lib.tool.unitsatisfy import unit_satisfy
from .base import BaseHandler
from ..base import EnsureUser


# root user is allowed to do ANYTHING, including path traversal attack
class UploadedHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.dash.file')

    NO_PERMISSION = 1
    SIZE_TOO_BIG = 2
    DUPLICATED_NAME = 4
    DECODE_ERROR = 8

    NOT_FOUND = 1
    DELETE_FAILED = 2

    type2icon = {
        'folder': 'am-icon-folder-o',
        'text': 'am-icon-file-text-o',
        'word': 'am-icon-file-word-o',
        'zip': 'am-icon-file-archive-o',
        'audio': 'am-icon-file-audio-o',
        'excel': 'am-icon-file-excel-o',
        'image': 'am-icon-file-image-o',
        'video': 'am-icon-file-video-o',
        'unknown': 'am-icon-file-o',
        'pdf': 'am-icon-file-pdf-o',
        'ppt': 'am-icon-file-powerpoint-o',
    }

    @EnsureUser(EnsureUser.ROOT)
    def get(self, path=None):
        # AGAIN, there could be path attack
        # BUT... tornado will prevent that?
        if not path:
            path = ''

        self.debug('path %r', path)
        folder = self.get_path_or_redirect(path)
        if folder is None:
            return

        self.debug(folder)

        return self.render(
            'tomorrow/dash/uploaded.html',
            contents=self.folder_attrs(folder),
            path=path,
            quote=quote,
        )

    def get_path_or_redirect(self, path):
        user = self.current_user
        name = user.name
        folder = os.path.join(self.config.root, 'static', 'tomorrow',
                                 name, path)
        if os.path.isfile(folder):
            self.redirect('/static/tomorrow/%s/%s' %
                          (quote(name, ''), path))
            return None
        elif os.path.isdir(folder) and path and not path.endswith('/'):
            self.redirect(urlsplit(self.request.uri).path + '/')
            return None

        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    def folder_attrs(self, path):
        dirpath, dirnames, filenames = next(os.walk(path))
        folder_icon = self.type2icon['folder']
        for folder in dirnames:
            yield  {'name': folder,
                    'icon': folder_icon,
                    'folder': True,
                    }

        for file_name in filenames:
            icon = self.icon(file_name)
            size = os.path.getsize(os.path.join(path, file_name))
            size_str = '%.2f %s' % unit_satisfy(size)
            yield {'name': file_name,
                   'icon': icon,
                   'size': size_str,
                   'folder': False,
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

    @EnsureUser(EnsureUser.ROOT)
    def post(self, path=None):
        self.check_xsrf_cookie()
        if not path:
            path = ''

        userinfo = self.current_user
        user = userinfo['user']
        type = userinfo['type']

        if type < User.admin:
            self.write(json.dumps({'error': self.NO_PERMISSION}))
            self.finish()
            return

        action = self.get_argument('action', 'upload')

        if action == 'upload':
            yield self.upload(to)
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
                self.error(e)
                error = self.DELETE_FAILED
        self.write(json.dumps({'error': error, 'name': filename}))
        self.finish()
        self.debug('deleted %s', filename)
        return

    @EnsureUser(EnsureUser.ROOT)
    def upload(self, to):
        user = self.current_user['user']
        urldata = self.get_argument('urldata')
        filename = self.get_argument('name')
        folder = os.path.join(self.get_user_path(user), to)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        mainurl = self.get_user_url(user)

        if os.path.exists(os.path.join(folder, filename)):
            self.write(json.dumps({'error': self.DUPLICATED_NAME}))
            self.finish()
            return
            # ext = os.path.splitext(filename)[-1]
            # mainname = time.strftime('%y-%m-%d-%H-%M-%S',
            #                          time.localtime(time.time()))
            # filename = mainname + ext
            #
            # if os.path.exists(os.path.join(folder, filename)):
            #     self.write(json.dumps({'error': self.DUPLICATED_NAME}))
            #     self.finish()
            #     return
        try:
            bindata = yield self.decode(urldata)
        except binascii.Error as e:
            self.error(e)
            self.write(json.dumps({'error': self.DECODE_ERROR}))
            self.finish()
            return

        yield self.save_file(os.path.join(folder, filename), bindata)

        self.write(json.dumps({
            'error': 0,
            'name': filename,
            'icon': self.icon(filename),
            'size': len(bindata),
            'url': urljoin(mainurl, quote('%s/%s' % (to, filename)))
        }))
        self.finish()
        self.info('saved %s', filename)
        return
