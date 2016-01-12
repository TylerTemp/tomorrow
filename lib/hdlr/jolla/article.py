import tornado.web
import tornado.escape
import logging
import time
import json
try:
    from urllib.parse import unquote, quote, urlsplit
except ImportError:
    from urllib import quote
    from urlparse import unquote, urlsplit
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from .base import BaseHandler
# import sys
# import os

# sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db.jolla import Article, Author, User
from lib.tool import md
from lib.config import Config
# sys.path.pop(0)

logger = logging.getLogger('jolla.article')

class ArticleHandler(BaseHandler):
    HOST = Config().main_host

    def get(self, slug):
        slug = unquote(slug)
        lang = self.locale.code[:2].lower()
        article = Article(slug, lang)
        if not article:
            raise tornado.web.HTTPError(404, "article %s not found" % slug)

        author = self.get_author(article)
        source = self.get_source(article)

        return self.render(
            'jolla/article.html',
            article=article,
            author=author,
            source=source,
            md2html=md.md2html,
            escape=tornado.escape.xhtml_escape,
            make_source=self.make_source,
        )

    def get_author(self, article):
        author = User(article.author, article.lang)
        return author

    def get_source(self, article):
        source = article.source
        if source:
            author = source['author']
            source['author'] = Author(author)

        return source

