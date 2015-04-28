import tornado.web
import tornado.gen
import logging
import json
try:
    from urllib.parse import quote
    from urllib.parse import unquote
except ImportError:
    from urlparse import quote
    from urlparse import unquote


import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.tool.md import md2html
from lib.tool.md import escape
from lib.db import Jolla
from lib.db import Article
from lib.db import User
from lib.config import Config
sys.path.pop(0)

cfg = Config()


class TranslateHandler(BaseHandler):

    def get(self, url):
        url = unquote(url)
        to_translate = Jolla.find_url(url)
        if to_translate is None:
            raise tornado.web.HTTPError(404,
                                        "the article to translate not found")

        self.xsrf_token

        translate = {
            'title': to_translate['title'],
            'md': to_translate['content'],
            'html': md2html(to_translate['content']),
        }

        userinfo = self.get_current_user()
        if userinfo is None:
            translated = None
            imgs = files = None
            username = usertype = None
            edit_task_url = None
        else:
            username = userinfo['user']
            usertype = userinfo['type']
            translated = Article.find_ref_of_user(url, username)
            imgs, files = self.get_imgs_and_files(username, usertype)
            if usertype >= User.admin:
                edit_task_url = '/jolla/task/' + quote(url)
            else:
                edit_task_url = None

        if translated is None:
            translated = {k: '' for k in translate.keys()}
        else:
            translated = {
                'title': translated['title'],
                'md': translated['content'],
                'html':md2html(translated['content']),
            }

        return self.render(
            'jolla/translate.html',
            translate=translate,
            translated=translated,
            user=username,
            imgs=imgs,
            files=files,
            edit_task_url=edit_task_url,
            img_upload_url=('/hi/%s/img/' % quote(username)
                            if username else None),
            file_upload_url=('/hi/%s/file/' % quote(username)
                             if username else None),
            size_limit=cfg.size_limit.get(usertype, 0),
            md=self.get_argument('md', False),
        )

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, url):
        self.check_xsrf_cookie()

        title = self.get_argument('title')
        format = self.get_argument('format')
        content = self.get_argument('content')

        url = unquote(url)
        to_translate = Jolla.find_url(url)
        if to_translate is None:
            raise tornado.web.HTTPError(404,
                                        "the article to translate not found")

        if format != 'md':
            content = html2md(content)
        else:
            content = escape(content)

        if self.get_current_user() is None:
            self.save_anonymous()
        else:
            self.save_logged()

        if translated is None:
            translated = Article()

            # board, title, content, author, email, url=None,
            # show_email=True, license=CC_LICENSE, transref=None, transinfo=None


    def save_anonymous(self):
        pass

    def save_logged(self):
        pass
