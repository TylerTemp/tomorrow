import logging
import tornado.web
import json
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
from .base import BaseHandler

from lib.db.jolla import Article, Source


class PostsHandler(BaseHandler):
    logger = logging.getLogger('jolla.posts')

    @tornado.web.authenticated
    def get(self):
        return self.render(
            'jolla/posts.html',
            articles=self.find_articles(self.current_user),
        )

    def find_articles(self, user):
        for each in Article.by_user(user._id):
            article = Article(lang=self.locale.code[:2])
            article.update(each)
            if article.source:
                link = article.source['link']
                article.edit_link = '/tr/?source=%s' % quote(link, '')
            else:
                article.edit_link = '/edit/%s/' % quote(article.slug)

            yield article

    @tornado.web.authenticated
    def post(self):
        article = Article(self.get_argument('slug'))
        if not article:
            raise tornado.web.HTTPError(404, '%r not found' % article.slug)

        if article.source:
            source = Source(article.source['link'])
            if source.translated == article.slug:
                source.translated = None
                source.save()

        delete_count = article.remove()
        assert delete_count == 1, \
            'delete %s of %s' % (delete_count, article.slug)

        self.write(json.dumps({'error': 0}))
