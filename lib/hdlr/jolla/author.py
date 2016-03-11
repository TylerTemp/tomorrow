import logging
import tornado.web
from bson import ObjectId
import os
try:
    from urllib.parse import unquote, quote, urlsplit
except ImportError:
    from urllib import quote
    from urlparse import unquote, urlsplit
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from .base import BaseHandler, EnsureUser

from lib.db.jolla import Article, Author


class AuthorHandler(BaseHandler):
    logger = logging.getLogger('jolla.article')

    @EnsureUser(EnsureUser.NORMAL)
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

        self.write({
            'name': author.name,
            'photo': author.photo,
            'intro': author.intro,
            'error': 0,
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

    @EnsureUser(EnsureUser.NORMAL)
    def post(self):
        self.check_xsrf_cookie()

        name = self.get_argument('name')
        author = Author(name)
        author.intro = self.get_argument('intro', '').rstrip() or None

        url, content = self.get_photo()

        if content:
            photo = content if url else self.save_photo(content, author.name)
        else:
            photo = None

        author.photo = photo

        author.save()

        self.write({
            'name': author.name,
            'photo': author.photo,
            'intro': author.intro,
            'error': 0,
        })

    def get_photo(self):
        files = self.request.files
        if 'photo' not in files:
            url_photo = self.get_argument('photo', '').strip() or None
            if url_photo:
                return True, url_photo
            else:
                return False, None

        f = files['photo'][0]
        content = f['body']
        return False, content

    def save_photo(self, content, name):

        path = os.path.join(self.config.root, 'static',
                            'author', name)

        with open(path, 'wb') as f:
            f.write(content)

        return '/static/author/%s' % name
