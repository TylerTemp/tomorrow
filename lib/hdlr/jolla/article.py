import tornado.web
import logging
import time
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urlparse import unquote
    from urlparse import quote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import Article
from lib.tool import md
sys.path.pop(0)

logger = logging.getLogger('tomorrow.jolla.article')

class ArticleHandler(BaseHandler):

    def get(self, url):
        url = unquote(url)
        article = Article(url)
        if article.new:
            raise tornado.web.HTTPError(404, "article %s not found" % url)

        result = self.parse_article(article.get())
        self.parse_html(result)

        return self.render(
            'jolla/article.html',
            article=result,
            headimg=result.pop('headimg'),
            license=result.pop('license'),
            createtime=result.pop('createtime'),
            await=result.pop('await'),
            reject=result.pop('reject'),
        )

    def parse_article(self, info):
        result = {
            'translated': {
                'title': info['title'],
                'author': info['author'],
                'email': info['email'],
                'showmail': info['show_email'],
                'content': info['content'],
            },
            'original': {
                'title': info['transinfo']['title'],
                'author': info['transinfo']['author'],
                'link': info['transinfo']['link'],
            },
            'headimg': info['transinfo']['headimg'],
            'license': info['license'],
            'createtime': info['createtime'],
            'reprint': info['transinfo']['reprint'],
            'await': info['transinfo']['status'] == Article.AWAIT,
            'reject': info['transinfo']['status'] == Article.REJECT,
        }
        return result

    def parse_html(self, info):
        info['translated']['content'] = md.md2html(
            info['translated']['content'])
        if info['translated'].pop('showmail'):
            info['translated']['emaillink'] = (
                '<a href="mailto: %s" rel="author">'
                    '<span class="am-icon-envelope"></span>'
                '</a>'
            ) % info['translated']['email']
        info['translated']['author'] = (
            '<a href="/hi/%s/" target="_blank" rel="author">%s</a>' % (
                quote(info['translated']['author']),
                info['translated']['author'])
        )

        info['createtime'] = (
            '<time>%s</time>' % time.strftime(
                "%Y-%m-%d", time.localtime(info['createtime']))
        )
