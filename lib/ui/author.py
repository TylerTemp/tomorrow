# coding: utf-8
import tornado.web
import logging

import sys
import os

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import JollaAuthor
sys.path.pop(0)

logger = logging.getLogger('tomorrow.ui.author')


class AuthorModule(tornado.web.UIModule):

    def render(self, name):
        author = JollaAuthor(name)
        if author.new:
            return ''
        return self.render_string(
            'uimodule/author.html',
            name=author.name,
            content=author.translation or author.description,
            img=author.photo,
        )
