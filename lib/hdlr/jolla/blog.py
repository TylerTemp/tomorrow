import tornado.web
import tornado.escape
import logging
import random
try:
    from urllib.parse import quote
    from urllib.parse import urlsplit
except ImportError:
    from urllib import quote
    from urlparse import urlsplit
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import Article
from lib.config import Config
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.jolla.blog')


class BlogHandler(BaseHandler):
    _cfg = Config()
    LIMIT = _cfg.jolla_post_limit
    HOST = _cfg.jolla_host

    def get(self, page=1):
        page = int(page)
        skip = (page - 1) * self.LIMIT
        limit = self.LIMIT
        result = Article.display_jolla(skip, limit)
        total = result.count()
        has_next_page = (page * limit < total)

        return self.render(
            'jolla/blog.html',
            articles=self.parse_jolla(result),
            this_page=page,
            has_next_page=has_next_page,
            # animate=self.random_animation_class,
        )

    def parse_jolla(self, collected):
        for each in collected:
            if 'transinfo' in each:
                main = self.get_source(each['transinfo']['link'])
            else:
                main = ('<span class="am-badge am-badge-warning">%s</span>' %
                        self.locale.translate('original'))

            tags = ' '.join(self.make_tag(each['tag']))

            des = each['zh']['description']
            if des is None:
                des = tornado.escape.xhtml_escape(each['zh']['content'][:80]) + '...'
            else:
                des = md2html(des)
            result = {
                'title': each['zh']['title'],
                'slug': '//%s/%s/' % (self.HOST, quote(each['slug'])),
                'img': each['cover'] or each['headimg'],
                'descripition': des,
                'source': main,
                'tag': tags
            }
            yield result

    def get_source(self, link):
        sp = urlsplit(link)
        netloc = sp.netloc
        if netloc in ('blog.jolla.com', 'together.jolla.com'):
            return '<span class="iconfont icon-jolla"> </span>'
        elif netloc == 'reviewjolla.blogspot.com':
            return '<img src="https://dn-jolla.qbox.me/reviewjolla.ico" style="display: inline">'
        elif netloc == 'www.jollausers.com':
            return '<img src="https://dn-jolla.qbox.me/jollausers.ico" style="display: inline">'
        else:
            sep = netloc.split('.')
            if len(sep) == 2:
                name = sep[0]
            elif len(sep) == 3:
                name = sep[1]
            else:
                name = netloc

            return '<span class="am-badge am-badge-secondary">%s</span>' % name

    def make_tag(self, tags):
        if tags:
            yield '|'
        for tag1, tag2 in zip_longest(tags[::2], tags[1::2]):
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

    animation_classes = [
        'fade', 'scale-up',
        'scale-down', 'slide-top',
        'slide-bottom', 'slide-left',
        'slide-right',
        # 'shake',
        # 'spin'
    ]

    # def random_animation_class(self):
    #     cls = self.animation_classes
    #     return random.choice(cls)