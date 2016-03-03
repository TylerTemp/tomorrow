import tornado.web
import logging
import json
import mimetypes
import os
try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote
    from urlparse import unquote

from .base import BaseHandler
from lib.tool.b64 import decode_data_url


class ProfileHandler(BaseHandler):
    logger = logging.getLogger('jolla.profile')

    @tornado.web.authenticated
    def get(self):

        return self.render(
            'jolla/profile.html',
            user=self.current_user
        )

    @tornado.web.authenticated
    def post(self):
        self.check_xsrf_cookie()
        user = self.current_user

        avatar_raw, ext = self.get_avatar()
        user.name = self.get_argument('name')
        user.email = self.get_argument('email', '').strip() or None
        user.home = self.get_argument('home', '').strip() or None

        zh = user.zh
        zh['intro'] = self.get_argument('zh-intro', '').rstrip() or None
        zh['donate'] = self.get_argument('zh-donate', '').rstrip() or None

        en = user.en
        en['intro'] = self.get_argument('en-intro', '').rstrip() or None
        en['donate'] = self.get_argument('en-donate', '').rstrip() or None

        if avatar_raw:
            photo = self.save_avatar(avatar_raw, ext)
            user.photo = photo

        user.save()

        self.write(json.dumps({
            'error': 0,
            'name': user.name,
            'email': user.email,
            'photo': user.photo,
            'zh_intro': user.zh.get('intro', None),
            'zh_donate': user.zh.get('donate', None),
            'en_intro': user.en.get('intro', None),
            'en_donate': user.en.get('donate', None),
        }))

    def get_avatar(self):
        direct = self.get_argument('avatar', None)
        ext = None
        if not direct:
            files = self.request.files
            if 'avatar' not in files:
                return None, None
            self.debug('from form')
            f = files['avatar'][0]
            content = f['body']
            name = f['filename']
            ext = os.path.splitext(name)[-1]
            if ext:
                ext = ext[1:]
        else:
            self.debug('from js encode')
            self.debug(repr(direct))
            content = decode_data_url(direct)
            mime, _ = mimetypes.guess_type(direct)
            if mime and '/' in mime:
                ext = mime.split('/')[-1]

        return content, ext

    def save_avatar(self, content, ext):
        name = str(self.current_user._id)
        if ext:
            name = '%s.%s' % (name, ext)

        fpath = os.path.join(self.config.root, 'static', 'jolla', 'avatar',
                             name)
        self.info('save to %s', fpath)
        with open(fpath, 'wb') as f:
            f.write(content)

        return '/static/jolla/avatar/%s' % name
