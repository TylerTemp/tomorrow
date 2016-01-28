import tornado.web
import tornado.escape
import logging
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

from lib.db.jolla import Article, Author, User, Redirect
from lib.tool import md

logger = logging.getLogger('jolla.article')

class ArticleHandler(BaseHandler):

    def get(self, slug):
        slug = unquote(slug)
        red = Redirect(slug)
        if red:
            return self.redirect('/%s/' % red.target)

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
