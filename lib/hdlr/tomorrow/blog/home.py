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
from lib.db import Article, User
from lib.config import Config
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.blog.home')


class HomeHandler(BaseHandler):
    _cfg = Config()
    LIMIT = _cfg.home_post_limit
    CHARS = _cfg.home_description_limit
    JOLLA = _cfg.jolla_host
    _u = User('TylerTemp').get()
    OWNER_IMG = _u['img']
    # HOST = _cfg.main_host

    def get(self, page=1):
        this_page = int(page)

        limit = self.LIMIT
        offset = limit * (this_page - 1)
        collected = Article.find_blog(offset, limit)

        total = collected.count()
        has_next_page = (this_page * limit < total)

        return self.render(
            'tomorrow/blog/home.html',
            nav_active='home',
            posts=self.parse_posts(collected),
            this_page=this_page,
            has_next_page=has_next_page,
            owner_img=self.OWNER_IMG
        )

    def parse_posts(self, collected):
        result = {}
        for each in collected:
            if 'zh' in each and 'en' in each:
                if self.locale.code[:2] == 'zh':
                    result['title'] = each['zh']['title']
                    result['content'] = each['zh']['content']
                    des = each['zh']['description']
                else:
                    result['title'] = each['en']['title']
                    result['content'] = each['en']['content']
                    des = each['en']['description']
            else:
                if 'zh' in each:
                    d = each['zh']
                else:
                    d = each['en']
                result['title'] = d['title']
                result['content'] = d['content']
                des = d['description']

            result['board'] = each['board']

            result['is_translation'] = ('transref' in each)
            result['cover'] = each.get('cover', None)

            if des is None:
                des = tornado.escape.xhtml_escape(
                    result['content'][:self.CHARS]) + '...'
            else:
                des = md2html(des)
            result['description'] = des
            result['author_name'] = each['author']
            result['author_link'] = '/hi/%s/' % quote(each['author'])
            result['post_time_attr'], result['post_time'] = \
                self.format_time(each['createtime'])
            quoted = quote(each['slug'])
            if each['board'] == 'jolla':
                link = '//%s/%s/' % (self.JOLLA, quoted)
                if 'transinfo' in each:
                    tag = ['jolla', 'tr']
                else:
                    tag = each['tag']
                    tag[:0] = ['jolla', 'original']
            else:
                link = '/blog/%s/' % quoted
                tag = each['tag']
            result['tag'] = ''.join(self.render_tags(tag))
            result['link'] = link
            yield result
            # yield each

    def format_time(self, t):
        t = time.localtime(t)
        attr = time.strftime('%Y-%m-%dT%H:%M:%S', t)
        display_time = time.strftime('%Y-%m-%d', t)
        return (attr, display_time)

    def render_tags(self, tags):
        for num, (tag1, tag2) in enumerate(zip_longest(tags[::2], tags[1::2])):
            if num > 3:
                yield '...'
                return
            first = ('<span class="am-badge am-badge-success am-radius">'
                     '%s'
                     '</span>') % self.locale.translate(tag1)
            yield first
            if tag2 is None:
                second = ''
            else:
                second = ('<span class="am-badge am-badge-primary am-radius">'
                          '%s'
                          '</span>') % self.locale.translate(tag2)
            yield second
