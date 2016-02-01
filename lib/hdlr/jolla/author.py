import logging
import tornado.web
from bson import ObjectId
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
        author = self.get_argument('load', None)
        if author:
            return self.render_load(author)

        self.xsrf_token
        return self.render(
            'jolla/author.html',
            authors=self.get_authors()
        )

    def render_load(self, name):
        author = Author(name)
        # if not author:
        #     raise tornado.web.HTTPError(404, 'Author %r not found' % name)

        self.write({
            'name': author.name,
            'photo': author.photo,
            'intro': author.intro,
        })

    def get_authors(self):
        author_found = set()
        for each in Article.collection.find({'source': {'$exists': True}}):
            source = each['source']
            author = source['author']
            if author not in author_found:
                author_found.add(author)

                this_author = Author(author)
                if not this_author:
                    this_author._id = ObjectId()
                yield this_author
        #
        # for each in Author.all():
        #     author = Author()
        #     author.update(each)
        #     yield author

    @tornado.web.authenticated
    def post(self):
        self.check_xsrf_cookie()