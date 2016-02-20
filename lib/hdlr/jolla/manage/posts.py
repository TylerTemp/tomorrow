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
            return self.load(self.get_article())

        return self.render(
            'jolla/manage/post.html',
            posts=self.get_posts()
        )

    @EnsureUser(EnsureUser.ROOT)
    def post(self):
        action = self.get_argument('action', None)
        if action == 'delete':
            return self.delete()

        article = self.get_article()
        article.slug = self.get_argument('slug')
        article.status = int(self.get_argument('status').strip())
        article.cover = self.get_argument('cover', '').strip() or None
        article.banner = self.get_argument('banner', '').strip() or None

        tags = []
        for each in self.get_argument('tag').split(','):
            tag = each.strip()
            if tag not in tags:
                tags.append(tag)
        article.tag = tags

        article.title = self.get_argument('zh-title', '').strip() or None
        article.description = self.get_argument('zh-description', '').strip() or None
        article.content = self.get_argument('zh-content', '').strip() or None

        en = article.en

        en_title = self.get_argument('en-title', '').strip() or None
        en_desc = self.get_argument('en-description', '').strip() or None
        en_content = self.get_argument('en-content', '').strip() or None
        if en_title:
            en['title'] = en_title
            en['description'] = en_desc
            en['content'] = en_content

        article.save()

        return self.load(article)

    def delete(self):
        self.get_article().remove()
        return self.write({'error': 0})

    def load(self, article):
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
