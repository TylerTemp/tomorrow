import logging
import pymongo
from lib.db.jolla import Source, Article
from ..base import BaseHandler, EnsureUser


class TranslateHandler(BaseHandler):
    logger = logging.getLogger('jolla.manage.translate')

    @EnsureUser(EnsureUser.ADMIN)
    def get(self):
        return self.render(
            'jolla/manage/translate.html',
            sources=self.all_source_with_count()
        )

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
