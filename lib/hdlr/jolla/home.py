import tornado.web
import tornado.escape
import logging
import json
try:
    from urllib.parse import quote, urlsplit
except ImportError:
    from urllib import quote
    from urlparse import urlsplit

from .base import BaseHandler

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db.jolla import Article
from lib.config import Config
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('jolla.home')


class HomeHandler(BaseHandler):
    _cfg = Config()
    LIMIT = _cfg.jolla_post_limit
    HOST = _cfg.jolla_host

    def get(self, page=1):
        render_json = (self.get_argument('format', None) == 'json')

        if render_json:
            skip = int(self.get_argument('offset', 0))
            limit = self.get_argument('limit', None)
            if limit is not None:
                limit = int(limit)
            # ahead_num = skip
        else:
            page = int(page)
            skip = (page - 1) * self.LIMIT
            limit = self.LIMIT
            # ahead_num = page * limit

        result = Article.all_shown(skip, limit)
        total = result.count()
        # current_rest_articles = (total - ahead_num)

        has_next_page = (page * limit < total)

        return self.render(
            'jolla/home.html',
            articles=self.get_articles(result),
            this_page=page,
            has_next_page=has_next_page,
            make_source=self.make_source,
            quote=quote,
            md2html=md2html,
            escape=tornado.escape.xhtml_escape,
        )

    def get_articles(self, result):
        for each in result:
            a = Article()
            a.update(each)
            yield a

    def formal(self, collected):
        is_empty = True
        for each in collected:
            is_empty = False
            if 'transinfo' in each:
                source_name = self.get_source_name(each['transinfo']['link'])
            else:
                source_name = None

            preview = tornado.escape.xhtml_escape(each['zh']['content'][:80])
            markdown_des = each['zh']['description']
            if markdown_des is None:
                des = None
            else:
                des = self.md_description_to_html(markdown_des)
            result = {
                'title': each['zh']['title'],
                'slug': quote(each['slug']),
                'link': '//%s/%s/' % (self.HOST, quote(each['slug'])),
                'img': each['cover'] or each['headimg'],
                'markdown_descripition': markdown_des,
                'descripition': des,
                'preview': preview,
                'source': source_name,
                'tag': each['tag']
            }
            yield result

        if is_empty:
            raise tornado.web.HTTPError(404, 'No posts on this page')