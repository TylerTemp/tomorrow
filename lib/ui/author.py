# coding: utf-8
import tornado.web
import logging
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

import sys
import os

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import JollaAuthor, User
from lib.tool.md import md2html
from lib.config import Config
sys.path.pop(0)

logger = logging.getLogger('tomorrow.ui.author')


class JollaAuthorModule(tornado.web.UIModule):

    def render(self, name):
        author = JollaAuthor(name)
        if author.new:
            return ''
        return self.render_string(
            'uimodule/jolla_author.html',
            name=author.name,
            content=author.translation or author.description or '',
            img=author.photo,
        )

class AuthorModule(tornado.web.UIModule):
    MAIN_HOST = Config().main_host

    def render(self, name):
        author = User(name)
        if author.new:
            return ''
        info = author.get()
        img = info['img']

        intro_info = info['intro']
        if intro_info['show_in_article']:
            intro = intro_info['content']
        else:
            intro = None

        donate_info = info['donate']
        if not donate_info['show_in_article']:
            donate = None
        elif donate_info['info']:
            donate = donate_info['old']
        else:
            donate = donate_info['new']

        return self.render_string(
            'uimodule/author.html',
            name=quote(name),
            img=img,
            intro=md2html(intro) if intro else None,
            donate=md2html(donate) if donate else None,
            MAIN_HOST=self.MAIN_HOST,
        )