import tornado.web
import logging
import mimetypes
import os
import shutil
try:
    from urllib.parse import unquote, quote, urljoin, urlsplit
except ImportError:
    from urllib import unquote, quote
    from urlparse import urljoin, urlsplit

from lib.tool.unitsatisfy import unit_satisfy
from .base import BaseHandler
from ..base import EnsureUser


# root user is allowed to do ANYTHING, including path traversal attack
class UploadedHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.dash.file')

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

        action = self.get_argument('action')
        if action == 'delete':
            return self.delete()
        elif action == 'move':
            return self.move()
        else:
            return self.save()

    def delete(self):
        path = self.get_argument('path')
        folder = os.path.join(self.config.root, 'static', 'tomorrow',
                              self.current_user.name, path)
        self.info('delete: %s', folder)

        try:
            shutil.rmtree(folder)
        except BaseException as e:
            msg = str(e)
            error = 1
        else:
            msg = None
            error = 0

        return self.write({'error': error, 'msg': msg})

    def move(self):
        src = self.get_argument('src')
        dist = self.get_argument('dist')
        root = os.path.join(self.config.root, 'static', 'tomorrow',
                            self.current_user.name)

        source = os.path.join(root, src)
        destination = os.path.join(root, dist)
        self.info('move: %s -> %s', source, destination)

        try:
            shutil.move(source, destination)
        except BaseException as e:
            message = str(e)
            error = 1
        else:
            message = None
            error = 0

        return self.write({'error': error, 'message': message})

    def save(self):
        path = self.get_argument('folder')
        file_bodys = self.request.files['file']
        status = []
        errors = []
        for each in file_bodys:
            name = each['filename']
            content = each['body']
            this_error = None
            try:
                with open(os.path.join(path, name), 'wb') as f:
                    f.write(content)
            except BaseException as e:
                this_error = str(e)
                errors.append((name, str(e)))
            size = len(content)


        error = 1 if errors else 0
        message = '; '.join('%s: %s' % x for x in errors)
        return self.write({'error': error, 'message': message,
                           errors: errors})
