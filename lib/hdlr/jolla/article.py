import tornado.web
import tornado.escape
import logging
import time
import re
try:
    from urllib.parse import unquote
    from urllib.parse import quote
    from urllib.parse import urlsplit
except ImportError:
    from urlparse import unquote
    from urlparse import quote
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
from lib.tool import md
from lib.config import Config
sys.path.pop(0)

logger = logging.getLogger('tomorrow.jolla.article')

class ArticleHandler(BaseHandler):
    HOST = Config().main_host

    def get(self, slug):
        slug = unquote(slug)
        article = Article(slug)
        if article.new:
            raise tornado.web.HTTPError(404, "article %s not found" % slug)

        result = self.parse_article(article.get())
        self.parse_html(result)

        return self.render(
            'jolla/article.html',
            article=result,
            headimg=result.pop('headimg'),
            createtime=result.pop('createtime'),
            await=result.pop('await'),
            reject=result.pop('reject')
        )

    def parse_article(self, info):
        result = {
            'title': info['zh']['title'],
            'author': info['author'],
            'email': info['email'],
            'showmail': info['show_email'],
            'tag': info['tag'],
            'content': info['zh']['content'],
            'original': None,
            'headimg': info['headimg'],
            'description': info['zh']['description'],
            'createtime': info['createtime'],
            'await': False,
            'reject': False,
            'id': str(info['_id'])
        }

        if 'transinfo' in info:
            result['original'] = {
                'title': info['transinfo']['title'],
                'author': info['transinfo']['author'],
                'link': info['transinfo']['link'],
            }
            result['await'] = info['transinfo']['status'] == Article.AWAIT
            result['reject'] = info['transinfo']['status'] == Article.REJECT

        return result

    p_re = re.compile(r'^<p>.*?</p>$')

    def parse_html(self, info):

        if info['original'] is not None:
            main = self.get_source(info['original']['link'])
        else:
            main = ('<span class="am-badge am-badge-warning">%s</span>' %
                        self.locale.translate('original'))
        tags = ' '.join(self.make_tag(info['tag']))

        info['source'] = main
        info['tag'] = tags

        info['content'] = md.md2html(info['content'])
        if info.pop('showmail'):
            info['emaillink'] = (
                '<a href="mailto: %s" rel="author">'
                    '<span class="am-icon-envelope"></span>'
                '</a>'
            ) % info['email']
        info['author'] = (
            '<a href="//%s/hi/%s/" target="_blank" rel="author">%s</a>' % (
                self.HOST,
                quote(info['author']),
                info['author'])
        )

        info['createtime'] = (
            '<time>%s</time>' % time.strftime(
                "%Y-%m-%d", time.localtime(info['createtime']))
        )

        if info['description'] is not None:
            info['description'] = md.md2html(info['description'])
            if self.p_re.match(info['description']):
                info['description'] = info['description'][3:-4]

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
