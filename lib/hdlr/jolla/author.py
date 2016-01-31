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

from lib.db.jolla import Article, Author

logger = logging.getLogger('jolla.article')


class AuthorHandler(BaseHandler):

    def get(self):
        return self.render(
            'jolla/author.html',
            authors=self.get_authors()
        )

    def get_authors(self):
        for each in Author.all():
            author = Author()
            author.update(each)
            yield author
