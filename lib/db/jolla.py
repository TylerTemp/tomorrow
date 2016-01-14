import pymongo
import logging
import time
# import sys
# import os
# sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
# from lib.db.base import Base
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
        'photo': None,
        'zh': {},  # intro, donate
        'en': {}
    }

    def __init__(self, _id=None, lang='zh'):
        super(User, self).__init__()
        self.__dict__['lang'] = lang
        if _id is not None:
            result = self.collection.find_one({'_id': _id})
            self.update(result)

    def __str__(self):
        return str(self.name)

    def __getattr__(self, item):
        if item == 'lang':
            return self.__dict__['lang']

        attrs = self.__dict__['__info__']
        if item in ('intro', 'donate'):
            target = attrs.get(self.lang, {})
            return target.get(item, None)

        return super(User, self).__getattr__(item)

    def __setattr__(self, item, value):
        if item == 'lang':
            self.__dict__['lang'] = value
            return

        attrs = self.__dict__['__info__']
        if item in ('intro', 'donate'):
            target = attrs.setdefault(self.lang, {})
            target[item] = value
            return

        return super(User, self).__setattr__(item, value)

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
        if slug:
            result = self.collection.find_one({'slug': slug})
            if result is None:
                self.slug = slug
            else:
                self.update(result)
        self.lang = lang

    def __getattr__(self, item):
        if item == 'lang':
            return self.__dict__.get('lang', 'zh')

        default = self._default
        attrs = self.__dict__['__info__']

        if item in ('title', 'content', 'description') and self.lang == 'en':
            en = self.en
            if en:
                return en[item]

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

    def lang_fit(self):
        lang = self.lang
        if lang == 'en':
            return lang in self.__dict__['__info__']

        return lang == 'zh'

    def _before_save(self):

        if self.create_time is None:
            self.create_time = time.time()
        self.edit_time = time.time()

        return super(Article, self)._before_save()

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

    @classmethod
    def all_shown(cls, offset=0, limit=None):
        result = cls.collection.find({'status': cls.ACCEPTED}).sort(
            (
             ('create_time', pymongo.DESCENDING),
            )
        )
        if limit is None:
            return result[offset:]
        return result[offset:offset + limit]


class Author(Base):
    collection = db.author

    _default = {
        '_id': None,
        'name': None,
        'photo': None,
        'introduce': None,
    }

    def __init__(self, name=None):
        super(Author, self).__init__()
        if name is not None:
            result = self.collection.find_one({'name': name})
            if result is None:
                self.name = name
            else:
                self.update(result)

    def __str__(self):
        return str(self.name)


class Source(Base):
    collection = db.source

    _default = {
        '_id': None,
        'link': None,  # required. Other attrs are only for suggestion
        'title': None,
        'author': None,
        'banner': None,
        'cover': None,
        'tag': [],
        'create_time': None,
        'slug': None,
        'translated': None,  # article slug
    }

    def __init__(self, link=None):
        super(Source, self).__init__()
        if link is not None:
            result = self.collection.find_one({'link': link})
            if result is None:
                self.link = link
            else:
                self.update(result)

    def _validate_attrs(self):
        if self.link is None:
            raise ValueError('link is missing')
        return super(Source, self)._validate_attrs()

    def _before_save(self):
        if self.create_time is None:
            self.create_time = time.time()
        return super(Source, self)._before_save()

if __name__ == '__main__':
    from bson import ObjectId

    logging.basicConfig(level=logging.DEBUG)
    _id = ObjectId('5695323ca27a133230936385')
    u = User(_id)
    print(u.intro)
    u.intro = 'test'
    print(u.intro)