import tornado.web
import logging

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import Article
sys.path.pop(0)

logger = logging.getLogger('tomorrow.jolla.blog')

class BlogHandler(BaseHandler):

    def get(self):
        return self.render(
            'jolla/blog.html',
            articles=self.get_trusted_jolla()
        )

    @classmethod
    def get_trusted_jolla(cls):
        for each in Article.find_jollas():
            if each['transinfo']['status'] != Article.TRUSTED:
                continue
            result = {
                'title': each['title'],
                'url': './%s' % each['url'],
                'img': each['transinfo']['headimg'],
                'preview': each['content'][:80],
            }
            yield result
