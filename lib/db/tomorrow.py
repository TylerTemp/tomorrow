import pymongo
import logging
import time
from passlib.hash import sha256_crypt
from bson import ObjectId
# import sys
# import os
# sys.path.insert(
#   0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.generate import generate
# from base import Base
from .base import Base



client = pymongo.MongoClient()
db = client['tomorrow']


class User(Base):
    collection = db.user
    logger = logging.getLogger('tomorrow.db.user')

    NORMAL = 0
    ROOT = 1

    NEWUSER = 1
    CHANGEEMAIL = 2
    CHANGEPWD = 4
    CHANGEUSER = 8

    OK = 0
    ERROR_NOT_APPLY = 1
    ERROR_WRONG = 2
    ERROR_OUT_OF_TIME = 3

    _default = {
        'name': None,
        'email': None,
        'pwd': None,
        # 'show_email': False,
        'type': NORMAL,
        'active': False,
        # 'intro': {},  # zh, en, show_in_home, show_in_article
        # 'donate': {},  # zh, en, show_in_home, show_in_article
        'photo': None,
        'app': [],  # [{'key', 'scope'}]
        'service': [],  # ['ss', '..']
        'verify': {'for': 0, 'code': 0, 'expire': None},
        '_id': None
    }

    # user
    # email
    # pwd
    # nickname
    # type
    def __init__(self, user_or_email=None, lang='zh'):
        super(User, self).__init__()
        attrs = self.__dict__['__info__']
        self.lang = lang
        if user_or_email is not None:
            key = 'email' if '@' in user_or_email else 'name'
            result = self.collection.find_one({key: user_or_email})
            if result is None:
                attrs[key] = user_or_email
            else:
                self.update(result)

    def __getattr__(self, item):
        if item == 'lang':
            return self.__dict__['lang']

        return super(User, self).__getattr__(item)

    def __setattr__(self, item, value):
        if item == 'lang':
            self.__dict__['lang'] = value
            return

        if item == 'pwd':
            self.__dict__['__info__']['pwd'] = sha256_crypt.encrypt(value)
            return

        return super(User, self).__setattr__(item, value)

    def _validate_attrs(self):
        for field, allowed in (
            # (self.intro, {'zh', 'en', 'show_in_home', 'show_in_article'}),
            # (self.donate, {'zh', 'en', 'show_in_home', 'show_in_article'}),
            (self.verify, {'code', 'for', 'expire'}),
        ):
            if not allowed.issuperset(field):
                raise ValueError('%s contains unexpected field(s) %s' %
                                 (list(field.keys()), allowed))

        return super(User, self)._validate_attrs()

    def _before_save(self):
        attrs = self.__dict__['__info__']
        if (not attrs.get('verify', None) or
                ('verify' in attrs and not attrs['verify']['code'])):
            attrs.pop('verify', None)
        return super(User, self)._before_save()

    def check_pwd(self, pwd):
        return sha256_crypt.verify(pwd, self.pwd)

    def remove(self):
        self.info('remove user %s', self._id)
        self.collection.delete_one({'_id': self._id})
        # self._user.remove({'user': self.user})
        self.__dict__['__info__'].clear()

    def authed_app(self, app_key):
        return self.collection.find_one({'app.key': app_key})

    @classmethod
    def generate(cls):
        collect = cls.collection
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

    def get(self, item):
        lang = self.lang
        target = getattr(self, item)
        other = 'en' if lang == 'zh' else 'zh'
        return target.get(lang, None) or target.get(other, None)

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
        return cls.collection.find({}).sort('create_time', pymongo.DESCENDING)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self.__dict__['__info__'])


class Article(Base):
    collection = db.article
    logger = logging.getLogger('tomorrow.db.article')
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

    def get(self, item):
        assert item in ('title', 'content', 'description')
        target = getattr(self, self.lang, None)
        if not target:
            check_lang = 'en' if self.lang == 'zh' else 'zh'
            target = getattr(self, check_lang)

        return target[item]

    def other_lang(self):
        lang = self.lang
        attrs = self.__dict__['__info__']
        other = 'en' if lang == 'zh' else 'zh'
        if attrs.get(other, False):
            return other
        return None

    def support_lang(self):
        lang = self.lang
        if self.__dict__['__info__'].get(lang, False):
            return lang

        return 'zh' if lang == 'en' else 'en'

    def lang_fit(self):
        lang = self.lang
        attrs = self.__dict__['__info__']
        return attrs.get(lang, False)

    @classmethod
    def by(self, author):
        return self.collection.find({'author': author})

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


class Auth(Base):
    collection = db.auth
    CODE_TIMEOUT = 60 * 10
    TOKEN_TIMEOUT = 60 * 60 * 24
    logger = logging.getLogger('tomorrow.db.auth')

    _default = {
        '_id': None,
        'key': None,
        'secret': None,
        'name': None,
        'callback': None,
        'image': None,
        'codes': [],  # [{'code': '', 'expire_at': time.time, 'uid': '...'}, ...]
        'tokens': [],  # [{'token': '', 'expire_at': '...', 'uid': '...'}]
    }

    def __init__(self, key=None):
        super(Auth, self).__init__()
        if key:
            result = self.collection.find_one({'key': key})
            if result is not None:
                self.update(result)
            else:
                self.key = key

    def generate_code(self):
        collection = self.collection
        while True:
            code = generate()
            if not collection.find_one({'codes.code': code}):
                return code

    def set_code(self, code, uid):
        expire_at = time.time() + self.CODE_TIMEOUT
        self.codes.append({'code': code, 'expire_at': expire_at, 'uid': uid})
        return expire_at

    def get_code(self, code):
        for each in self.codes:
            if each['code'] == code:
                return each

        self.warning('code %s of %s not found', code, self.name)
        return None

    def clear_code(self, code, save=False):
        self.debug('clear code %s', code)
        to_delete = []
        for index, each in enumerate(self.codes):
            if each['code'] == code:
                to_delete.append(index)

        if not to_delete:
            self.warning('code %s of %s not found', code, self.name)
            return False

        for each in to_delete[::-1]:
            self.codes.pop(each)

        if save:
            self.save()

        return True

    def generate_token(self):
        collection = self.collection
        while True:
            token = generate()
            if not collection.find_one({'tokens.token': token}):
                return token

    def set_token(self, token, uid):
        tokens = self.tokens
        expire_at = time.time() + self.TOKEN_TIMEOUT
        tokens.append({'token': token, 'expire_at': expire_at, 'uid': uid})
        return expire_at

    def clear_token(self, token, save=False):
        self.debug('clear token %s', token)
        to_delete = []
        for index, each in enumerate(self.codes):
            if each['code'] == token:
                to_delete.append(index)

        if not to_delete:
            self.warning('code %s of %s not found', token, self.name)
            return False

        for each in to_delete[::-1]:
            self.codes.pop(each)

        if save:
            self.save()

        return True
