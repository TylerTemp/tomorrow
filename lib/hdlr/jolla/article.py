import tornado.web
import tornado.escape
import logging
import base64
try:
    from urllib.parse import unquote, quote, urlsplit
except ImportError:
    from urllib import quote
    from urlparse import unquote, urlsplit
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

import pymongo
from .base import BaseHandler

from lib.db.jolla import Article, Author, User, Redirect, Comment
from lib.tool.timetool import w3c_datetime_full, timestamp_readable

try:
    import hashlib
except ImportError:
    import md5


    def str_to_md5_str(content):
        return base64.urlsafe_b64encode(md5.new(content.encode('utf-8')).digest())

else:


    def str_to_md5_str(content):
        return base64.urlsafe_b64encode(hashlib.md5(content.encode('utf-8')).digest())


class ArticleHandler(BaseHandler):
    logger = logging.getLogger('jolla.article')

    def get(self, slug):
        slug = unquote(slug)

        red = Redirect(slug)
        if red:
            return self.redirect('/%s/' % red.target, red.permanent)

        lang = self.locale.code[:2].lower()
        article = Article(slug, lang)
        if not article:
            raise tornado.web.HTTPError(404, "article %s not found" % slug)

        if not article.lang_fit():
            article.lang = article.other_lang()

        author = self.get_author(article)
        source = self.get_source(article)
        comments = self.get_comments(article)

        return self.render(
            'jolla/article.html',
            article=article,
            comments=comments,
            author=author,
            source=source,
            md2html=self.md2html,
            escape=tornado.escape.xhtml_escape,
            make_source=self.make_source,
            F_w3c_datetime_full=w3c_datetime_full,
            F_timestamp_readable=timestamp_readable,
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

    def get_comments(self, article):
        article_id = article._id
        sort = (
         ('create_time', pymongo.DESCENDING),
        )
        comments = Comment.find({'article_id': article_id}, _sort=sort)
        for comment in comments:
            comment.update({
                'avatar_slug': str_to_md5_str(comment.ip),
            })
            yield comment
