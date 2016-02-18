import logging
import pymongo
from bson import ObjectId
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
from ..base import BaseHandler, EnsureUser
from lib.db.jolla import Article


class PostHandler(BaseHandler):
    logger = logging.getLogger('jolla.manage.posts')

    @EnsureUser(EnsureUser.ROOT)
    def get(self):
        action = self.get_argument('action', None)
        if action == 'load':
            return self.load()

        return self.render(
            'jolla/manage/post.html',
            posts=self.get_posts()
        )

    @EnsureUser(EnsureUser.ROOT)
    def post(self):
        action = self.get_argument('action', None)
        if action == 'delete':
            return self.delete()

    def delete(self):
        self.get_article().remove()
        return self.write({'error': 0})

    def load(self):
        article = self.get_article()
        en = article.en
        info = {
            'slug': article.slug,
            'status': article.status,
            'cover': article.cover,
            'banner': article.banner,
            'tag': article.tag,
            'zh': {
                'title': article.title,
                'content': article.content,
                'description': article.description,
            },
            'en': {
                'title': en.get('title', None),
                'content': en.get('content', None),
                'description': en.get('description', None),
            }
        }

        return self.write(info)

    def get_article(self):
        _id = ObjectId(self.get_argument('id'))
        article = Article.find_one({'_id': _id})
        assert article, 'article %r not found' % _id
        return article

    def get_posts(self):
        return Article.find(
            {'source.link': {'$exists': False}},
            sort=[('create_time', pymongo.DESCENDING)])
