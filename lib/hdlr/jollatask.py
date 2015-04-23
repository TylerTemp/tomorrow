import tornado.web
import logging
import json
try:
    from urllib.parse import quote
    from urllib.parse import urljoin
except ImportError:
    from urlparse import quote
    from urlparse import urljoin

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.config import Config
from lib.db import Article
from lib.db import User
sys.path.pop(0)

cfg = Config()


class TaskHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, title=None):
        self.xsrf_token
        user_info = self.get_current_user()
        username = user_info['user']
        usertype = user_info['type']

        imgs, files = self.get_imgs_and_files(
            username, usertype)

        if title is not None:
            html, md = self.get_html_and_md(title)
        else:
            html, md = '', ''

        return self.render(
            'jollatask.html',
            imgs=imgs,
            files=files,
            title=title or '',
            html=html,
            md=md,
            img_upload_url='/hi/%s/img/' % quote(username),
            file_upload_url='/hi/%s/file/' % quote(username),
            size_limit=cfg.size_limit[usertype]
        )

    def get_imgs_and_files(self, user, type):
        allow_update = (type >= User.admin)
        if not allow_update:
            return None, None
        path = self.get_user_path(user)
        link = self.get_user_url(user)
        imgs = self.list_path(os.path.join(path, 'img'))
        files = self.list_path(os.path.join(path, 'file'))
        img_name_and_link = {
            name: urljoin(link, 'img/%s' % quote(name))
            for name in imgs}

        file_name_and_link = {
            name: urljoin(link, 'file/%s' % quote(name))
            for name in files}

        return img_name_and_link, file_name_and_link

    def list_path(self, path):
        if not os.path.exists(path):
            return []
        for dirpath, dirnames, filenames in os.walk(path):
            return list(filenames)

    def get_html_and_md(self, title):
        # todo: get
        return '', ''
