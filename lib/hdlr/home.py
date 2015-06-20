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

    def get(self, page=1):
        this_page = int(page)
        # count with skip won't work. WHY?
        # todo: better way to check next page
        posts = self.get_posts(self.LIMIT * (this_page - 1), self.LIMIT + 1)

        return self.render(
            'home.html',
            nav_active='home',
            posts=posts,
            this_page=this_page,
            limit=self.LIMIT)

    def get_posts(self, offset=0, limit=None):
        if limit is None:
            limit = self.LIMIT
        result = {}
        for each in Article.find_need_shown(offset, limit):
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
            result['post_time'], result['post_time_attr'] = \
                self.format_time(each['createtime'])
            if each['board'] == 'jolla':
                link = '/jolla/blog/%s/'
            else:
                link = '/post/%s/'
            result['link'] = link % quote(each['url'])
            yield result
            # yield each

    def format_time(self, t):
        t = time.localtime(t)
        attr = time.strftime('%Y-%m-%dT%H:%M:%S', t)
        display_time = time.strftime('%Y-%m-%d', t)
        return (attr, display_time)
