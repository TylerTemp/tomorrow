import tornado.locale
import tornado.web
try:
    from urllib.parse import unquote
except ImportError:
    from urlparse import unquote

import os
import sys

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.tool.md import md2html
from lib.db import Article
sys.path.pop(0)

class BreyHandler(BaseHandler):

    def get(self, slug=None):
        if slug is None:
            page_title = 'Hi Brey!'
            article_slug = 'brey-home'
        else:
            slug = unquote(slug)
            page_title = None
            article_slug = 'brey-' + slug

        article_result = Article(article_slug)
        if article_result.new:
            raise tornado.web.HTTPError(404, 'page "%s" not found' % slug)
        article = article_result.get()['en']
        if page_title is None:
            page_title = article['title']

        return self.render(
            'brey/brey.html',
            slug=slug,
            page_title=page_title,
            title=article['title'],
            content=md2html(article['content'])
        )

    def get_user_locale(self):
        return tornado.locale.get('en')

    def write_error(self, status_code, **kwargs):
        msg = self.get_error(status_code, **kwargs)

        return self.render(
            'brey/error.html',
            code=status_code,
            msg=msg,
        )