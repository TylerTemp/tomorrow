import tornado.locale
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

        article = Article(article_slug).get()['en']
        if page_title is None:
            page_title = '%s | Hi Brey' %  article['title']

        return self.render(
            'brey.html',
            slug=slug,
            page_title=page_title,
            title=article['title'],
            content=md2html(article['content'])
        )

    def get_user_locale(self):
        return tornado.locale.get('en')