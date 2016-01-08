import tornado.web
import tornado.escape
import logging
import json
import time
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from .base import BaseHandler
import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db.tomorrow import Article, User
from lib.config import Config
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.blog.home')


class HomeHandler(BaseHandler):
    _cfg = Config()
    LIMIT = _cfg.home_post_limit
    CHARS = _cfg.home_description_limit
    JOLLA = _cfg.jolla_host
    _u = User('TylerTemp')
    OWNER_IMG = _u.img
    # HOST = _cfg.main_host

    def get(self, page=1):
        this_page = int(page)

        limit = self.LIMIT
        offset = limit * (this_page - 1)
        collected = Article.all(offset, limit)

        total = collected.count()
        has_next_page = (this_page * limit < total)

        return self.render(
            'tomorrow/blog/home.html',
            posts=self.parse_posts(collected),
            this_page=this_page,
            has_next_page=has_next_page,
            quote=quote,
            md2html=md2html,
            escape=tornado.escape.xhtml_escape,
            owner_img=self.OWNER_IMG
        )

    def parse_posts(self, collected):
        for each in collected:
            lang = self.locale.code[:2]
            article = Article(lang=lang)
            article.update(each)
            yield article