import tornado.web
import logging
import json
import time
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import Article
from lib.config import Config
sys.path.pop(0)

logger = logging.getLogger('tomorrow.home')


class HomeHandler(BaseHandler):
    _cfg = Config()
    LIMIT = _cfg.home_post_limit
    CHARS = _cfg.home_description_limit
    JOLLA = _cfg.jolla_host
    # HOST = _cfg.main_host

    def get(self, page=1):
        this_page = int(page)

        limit = self.LIMIT
        offset = limit * (this_page - 1)
        collected = Article.find_need_shown(offset, limit)

        total = collected.count()
        has_next_page = (this_page * limit < total)

        return self.render(
            'home.html',
            nav_active='home',
            posts=self.parse_posts(collected),
            this_page=this_page,
            has_next_page=has_next_page
        )

    def parse_posts(self, collected):
        result = {}
        for each in collected:
            result['title'] = each['title']
            result['board'] = each['board']
            result['is_translation'] = ('transref' in each)
            cover = each.get('cover', None)
            if cover is None and 'transinfo' in each:
                transinfo = each['transinfo']
                cover = (transinfo.get('cover', None) or
                         transinfo.get('headimg', None))
            result['cover'] = cover
            result['description'] = (each.get('description', None) or
                                     each['content'][:self.CHARS] + '...')
            result['author_name'] = each['author']
            result['author_link'] = '/hi/%s/' % quote(each['author'])
            result['post_time_attr'], result['post_time'] = \
                self.format_time(each['createtime'])
            quoted = quote(each['url'])
            if each['board'] == 'jolla':
                link = '//%s/%s/' % (self.JOLLA, quoted)
            else:
                link = '/post/%s/' % quoted
            result['link'] = link
            yield result
            # yield each

    def format_time(self, t):
        t = time.localtime(t)
        attr = time.strftime('%Y-%m-%dT%H:%M:%S', t)
        display_time = time.strftime('%Y-%m-%d', t)
        return (attr, display_time)
