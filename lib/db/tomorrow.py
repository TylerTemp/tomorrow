import pymongo
import logging
from passlib.hash import sha256_crypt
from bson import ObjectId
# import sys
# import os
# sys.path.insert(
#   0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.generate import generate
# from base import Base
from .base import Base

logger = logging.getLogger('db.tomorrow')
client = pymongo.MongoClient()
db = client['tomorrow']


class User(Base):
    collection = db.user

    NORMAL = 0
    ADMIN = 1
    ROOT = 2

    NEWUSER = 1
    CHANGEEMAIL = 2
    CHANGEPWD = 4
    CHANGEUSER = 8

    OK = 0
    ERROR_NOT_APPLY = 1
    ERROR_WRONG = 2
    ERROR_OUT_OF_TIME = 3

    _default = {
        'user': None,
        'email': None,
        'pwd': None,
        'show_email': False,
        'type': NORMAL,
        'active': False,
        'intro': {},  # zh, en, show_in_home, show_in_article
        'donate': {},  # zh, en, show_in_home, show_in_article
        'photo': None,
        'app': [],  # [{'key', 'scope'}]
        'service': [],  # ['ss', '..']
        'verify': {},  # {'for': int, 'code': str, 'expire': float}
        '_id': None
    }

    # user
    # email
    # pwd
    # nickname
    # type
    def __init__(self, user_or_email=None):
        super(User, self).__init__()
        attrs = self.__dict__['__info__']
        if user_or_email is not None:
            key = 'email' if '@' in user_or_email else 'user'
            result = self.collection.find_one({key: user_or_email})
            if result is None:
                attrs[key] = user_or_email
            else:
                self.update(result)

    def __getattr__(self, item):
        default = self._default
        attrs = self.__dict__['__info__']

        if item not in attrs and item in default:
            default_val = default[item]
            if default_val == {}:
                attrs[item] = default_val = {}  # re-bind to a new dict
            elif default_val == []:
                attrs[item] = default_val = []
            return default_val

        return super(User, self).__getattr__(item)

    @property
    def pwd(self):
        return self.__dict__['__info__'].get('pwd', None)

    @pwd.setter
    def pwd(self, value):
        v = sha256_crypt(value)
        self.__dict__['__info__']['pwd'] = v

    def verity(self, pwd):
        sha256_crypt.verify(pwd, self.pwd)

    def _validate_attrs(self):
        for field, allowed in (
            (self.intro, {'zh', 'en', 'show_in_home', 'show_in_article'}),
            (self.donate, {'zh', 'en', 'show_in_home', 'show_in_article'}),
            (self.verify, {'code', 'for', 'expire'})
        ):
            if not allowed.issuperset(field):
                raise ValueError('%s contains unexpected field(s) %s' %
                                 (list(field.keys()), allowed))

        return super(User, self)._validate_attrs()

    def check_pwd(self, pwd):
        encoded_pwd = self.user_info['pwd']
        return sha256_crypt.verify(pwd, encoded_pwd)

    def remove(self):
        logger.info('remove user %s', self._id)
        self.collection.delete_one({'_id': self._id})
        # self._user.remove({'user': self.user})
        self.__dict__['__info__'].clear()

    def authed_app(self, app_key):
        return self.collection.find_one({'app.key': app_key})

    @classmethod
    def generate(cls):
        collect = cls._user
        while True:
            code = generate()
            if collect.find_one({'verify.code': code}) is None:
                return code

    def set_code(self, for_, code, expire=None):
        self.verify = {
            'for': for_,
            'code': code
        }
        if expire is not None:
            self.verify['expire'] = expire

    @classmethod
    def by_code(cls, code):
        info = cls.collection.find_one({'verify.code': code})
        if info is None:
            return None
        self = cls()
        self.update(info)
        return self

    @classmethod
    def by_id(cls, _id):
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        info = cls.collection.find_one({'_id': _id})
        if info is None:
            return None
        self = cls()
        self.update(info)
        return self

    @classmethod
    def all(cls):
        return cls.collection.find({}).sort('user', pymongo.DESCENDING)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self.__dict__['__info__'])


class Article(Base):
    collection = db.article
    _default = {
        '_id': None,
        'slug': None,
        'author': None,
        'email': None,
        'zh': {},
        'en': {},
        'show_email': None,
        'create_time': None,
        'edit_time': None,
        'cover': None,
        'banner': None,
        'tag': []
    }
    # slug:
    # author
    # email
    # zh/en = {title: ,content: ,description}
    # show_email: True/False
    # create_time
    # edit_time
    # tag: []

    def __init__(self, slug=None, lang='zh'):
        super(Article, self).__init__()
        self.lang = lang
        attrs = self.__dict__['__info__']
        if slug:
            result = self.collection.find_one({'slug': slug})
            if result is None:
                attrs['slug'] = slug
            else:
                self.update(result)

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
        if key in ('title', 'content', 'description'):
            lang = self.lang
            target = attrs.setdefault(lang, {})
            target[key] = value
            return

        return super(Article, self).__setattr__(key, value)

    def lang_fitted(self):
        return self.lang in self.__dict__['__info__']

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

class Message(Base):
    pass


class Auth(Base):
    pass


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    u = User('TylerTemp')
    print(u._id)
    u._id = 3
    u.x = 4
    u.save()
