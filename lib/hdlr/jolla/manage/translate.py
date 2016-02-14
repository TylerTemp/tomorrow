import logging
import pymongo
import tornado.web
import tornado.escape
from bson import ObjectId
from lib.db.jolla import Source, Article, User
from ..base import BaseHandler, EnsureUser
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


class TranslateHandler(BaseHandler):
    logger = logging.getLogger('jolla.manage.translate')

    @EnsureUser(EnsureUser.ADMIN)
    def get(self):
        action = self.get_argument('action', None)
        if action == 'load':
            return self.load()
        elif action == 'delete':
            return self.delete()
        elif action == 'load-article':
            return self.load_article()

        return self.render(
            'jolla/manage/translate.html',
            sources=self.all_source_with_count()
        )

    def load(self):
        _id = ObjectId(self.get_argument('id'))
        source = Source.find_one({'_id': _id})
        if not source:
            raise tornado.web.HTTPError(404, 'source %r not found' % _id)

        translates = []
        for slug, title, translator in self.get_translate_of(source.link):
            translates.append({'slug': slug, 'title': title,
                               'translator': translator})

        if source.translated:
            a = Article(source.translated, 'zh')
        else:
            a = Article()

        translate = self.get_article_info(a)

        return self.write({
            'title': source.title or tornado.escape.xhtml_escape(source.link),
            'edit': '/task/?source=%s' % quote(source.link, ''),
            'translate': translate,
            'translated': source.translated,
            'translates': translates,
        })

    def get_article_info(self, article):
        return {
            'title': article.title,
            'content': article.content,
            'description': article.description,
            'cover': article.cover,
            'banner': article.banner,
            'tag': article.tag,
            'slug': article.slug
        }

    def get_translate_of(self, link):
        for each in Article.collection.find({'source.link': link}):
            author = User(each['author'])
            yield each['slug'], each['title'], author.name

    def all_source_with_count(self):
        for each in Source.find(
                {'translated': {'$exists': False}},
                sort=[('create_time', pymongo.DESCENDING)]):
            yield each, self.get_trans_count(each.link)

        for each in Source.find(
                {'translated': {'$exists': True}},
                sort=[('create_time', pymongo.DESCENDING)]
            ):
            yield each, self.get_trans_count(each.link)

    def get_trans_count(self, link):
        return Article.collection.find({'source.link': link}).count()

    def load_article(self):
        a = Article(self.get_argument('slug'))
        if not a:
            raise tornado.web.HTTPError(404, 'Translation %r not found' %
                                        a.slug)

        return self.write(self.get_article_info(a))

    @EnsureUser(EnsureUser.ADMIN)
    def post(self):
        source = Source.find_one(
            {'_id': ObjectId(self.get_argument('source'))})
        assert source

        trans = self.get_argument('trans').strip()
        if not trans:
            article = Article(source.translated)
            source.translated = None
            Article.eject_except(source.link, None, Article.AWAIT)
            source.save()
            return self.write(self.get_article_info(Article()))

        article = Article(trans)
        assert article

        article.slug = self.get_argument('slug')
        article.banner = self.get_argument('banner').strip() or None
        article.cover = self.get_argument('cover').strip() or None
        article.description = self.get_argument('description').rstrip() or None
        article.content = self.get_argument('content').rstrip() or None
        tags = []
        for each in self.get_argument('tag').split(','):
            tag = each.strip()
            if tag not in tags:
                tags.append(tag)

        article.tag = tags

        source.translated = article.slug

        Article.eject_except(source.link, article._id)

        source.save()
        article.save()

        return self.write({'error': 0})