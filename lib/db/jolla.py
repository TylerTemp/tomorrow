import pymongo
import logging
# import sys
# import os
# sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
# from base import Base
from .base import Base

logger = logging.getLogger('db.jolla')
client = pymongo.MongoClient()
db = client['jolla']


class User(Base):
    collection = db.user

    TOMORROW = 'https://tomorrow.comes.today'

    _default = {
        '_id': None,
        'source': None,  # source site
        'uid': None,    # source site uid
        'email': None,
        'home': None,
        'name': None,
    }

    def __init__(self, _id=None):
        super(User, self).__init__()
        if _id is not None:
            result = self.collection.find_one({'_id': _id})
            self.update(result)

    @classmethod
    def by_source_id(cls, source, uid):
        result = cls.collection.find_one(
                {'source': source, 'uid': uid})
        self = cls()
        self.update(result)
        return self


class Article(Base):
    collection = db.article

    AWAIT = 0
    ACCEPTED = 1
    EJECTED = 2

    _default = {
        '_id': None,
        'slug': None,
        'status': AWAIT,
        'author': None,  # _id in User
        'title': None,
        'description': None,
        'content': None,
        'create_time': None,
        'edit_time': None,
        'cover': None,
        'banner': None,
        'tag': [],
        'source': {},  # link, title, author
        'en': {},  # title, description
    }

    def __init__(self, slug=None, lang='zh'):
        super(Article, self).__init__()
        attrs = self.__dict__['__info__']
        if slug:
            result = self.collection.find_one({'slug': slug})
            if result is None:
                attrs['slug'] = slug
            else:
                self.update(result)
        self.lang = lang

    def __getattr__(self, item):
        if item == 'lang':
            return self.__dict__.get('lang', 'zh')

        default = self._default
        attrs = self.__dict__['__info__']

        if item in ('title', 'content', 'description'):
            lang = self.lang
            return attrs.get(lang, {}).get(item, None)

        if item not in attrs and item in default:
            default_val = default[item]
            if default_val == {}:
                attrs[item] = default_val = {}  # re-bind to a new dict
            elif default_val == []:
                attrs[item] = default_val = []
            return default_val

        return super(Article, self).__getattr__(item)

    def __setattr__(self, key, value):
        if key == 'lang':
            self.__dict__[key] = value
            return

        attrs = self.__dict__['__info__']
        if self.lang == 'en' and key in ('title', 'content', 'description'):
            target = attrs.setdefault('en', {})
            target[key] = value
            return

        return super(Article, self).__setattr__(key, value)

    def lang_fitted(self):
        lang = self.lang
        if lang == 'en':
            return lang in self.__dict__['__info__']

        return lang == 'zh'

    @classmethod
    def all(cls, offset=0, limit=None):
        result = cls.collection.find({}).sort(
            (
             ('create_time', pymongo.DESCENDING),
            )
        )
        if limit is None:
            return result[offset:]
        return result[offset:offset + limit]


class Author(Base):
    pass