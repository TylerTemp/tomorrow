import tornado.web
import logging

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import Article
from lib.config import Config
sys.path.pop(0)

logger = logging.getLogger('tomorrow.jolla.blog')

class BlogHandler(BaseHandler):
    LIMIT = Config().jolla_post_limit

    def get(self, page=1):
        page = int(page)
        skip = (page - 1) * self.LIMIT
        limit = self.LIMIT
        result = Article.find_trusted_jollas(skip, limit)
        total = result.count()
        has_next_page = (page * limit < total)

        return self.render(
            'jolla/blog.html',
            articles=self.parse_jolla(result),
            this_page=page,
            has_next_page=has_next_page
        )

    @classmethod
    def parse_jolla(cls, collected):
        for each in collected:
            result = {
                'title': each['title'],
                'url': './%s' % each['url'],
                'img': each['transinfo']['headimg'],
                'descripition': (each['transinfo'].get('description', None)
                            or each['content'][:80] + '...'),
            }
            yield result
