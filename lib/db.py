'''
Usage:
    db.py [options]

Options:
    -u --user <user>     User name
    -p --pwd <pwd>       Password
    -e --email <email>   Email
    -t --type <type>     User type
    -a --add             Add new user
    -d --delete          Delete the user
'''
# todo: asynchronization

import pymongo
import logging
from bson.objectid import ObjectId
from passlib.hash import sha256_crypt
import time

import sys
import os

rootdir = os.path.normpath(os.path.join(__file__, '..', '..'))
sys.path.insert(0, rootdir)
from lib.tool import generate
sys.path.pop(0)

logger = logging.getLogger('tomorrow.db')

client = pymongo.MongoClient()
db = client['tomorrow']


class User(object):
    _user = db.user

    normal = 0
    admin = 1
    root = 2

    NEWUSER = 1
    CHANGEEMAIL = 2
    CHANGEPWD = 4
    CHANGEUSER = 8

    OK = 0
    ERROR_NOT_APPLY = 1
    ERROR_WRONG = 2
    ERROR_OUT_OF_TIME = 3

    # user
    # email
    # pwd
    # nickname
    # type
    def __init__(self, user_or_email=None):
        if user_or_email is None:
            self.user_info = None
            self.user = None
            self.email = None
        else:
            self.user_info = self.find_user(user_or_email)
            if self.user_info is None:
                self.user = user_or_email if '@' not in user_or_email else None
                self.email = user_or_email if '@' in user_or_email else None
            else:
                self.user = self.user_info['user']
                self.email = self.user_info['email']

    def add(self, user=None, email=None, pwd=None, type=None,
            show_email=True, active=False):
        if pwd:  # allow user inviting. So no pwd before active
            pwd = sha256_crypt.encrypt(pwd)
        user = user or self.user
        email = email or self.email
        assert email  # when inviting, only email is used
        logger.info('new user %s', user)
        type = self.normal if type is None else type
        self.user_info = {
            'user': user,
            'email': email,
            'pwd': pwd,
            'show_email': show_email,
            'type': type,
            'active': active
        }
        return self.user_info

    def verify(self, pwd):
        encoded_pwd = self.user_info['pwd']
        return sha256_crypt.verify(pwd, encoded_pwd)

    @classmethod
    def find_user(cls, user_or_email):
        if '@' in user_or_email:
            key = 'email'
        else:
            key = 'user'
        return cls._user.find_one({key: user_or_email})

    def remove(self):
        logger.info('remove user %s', self.user_info)
        self._user.delete_one({'_id': self.user_info['_id']})
        # self._user.remove({'user': self.user})
        self.user_info = None

    def set_img(self, url):
        self.user_info['img'] = url

    def save(self):
        info = self.user_info
        if '_id' in info:
            result = self._user.find_one_and_replace(
                {'_id': info['_id']},
                info)
        else:
            result = self._user.insert_one(self.user_info)
            self.user_info['_id'] = result
        return result

    def get(self):
        return self.user_info

    @classmethod
    def generate(cls):
        collect = cls._user
        while True:
            code = generate.generate()
            if collect.find_one({'verify.code': code}) is None:
                return code

    def set_code(self, for_, code, expire=None):
        info = self.user_info
        assert info
        info['verify'] = {
            'for': for_,
            'code': code
        }
        if expire is not None:
            info['verify']['expire'] = expire

    @classmethod
    def init_by_code(cls, code):
        info = cls._user.find_one({'verify.code': code})
        u = cls()
        u.user_info = info
        u.user = info['user'] if info else None
        u.email = info['email'] if info else None
        return u

    @classmethod
    def init_by_id(cls, _id):
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        info = cls._user.find_one({'_id': _id})
        u = cls()
        u.user_info = info
        u.user = info['user'] if info else None
        u.email = info['email'] if info else None
        return u

    @classmethod
    def get_collect(cls):
        return cls._user

    @classmethod
    def all(self):
        return self._user.find({})

    @property
    def new(self):
        return self.get() is None

    def __str__(self):
        if self.new:
            return 'new User(%s)' % self.user
        return str(self.user_info)

    def __repr__(self):
        if self.new:
            return 'User(%s)' % self.user
        return repr(self.user_info)


class Message(object):
    _msg = db.message

    def __init__(self, _id=None):
        self._id = _id
        if _id is None:
            self.from_ = self.to = self.content = self.time = None
        else:
            result = self._msg.find_one({'_id': _id})
            if result is None:
                self.from_ = self.to = self.content = self.time = None
            else:
                self.from_ = result['from']
                self.to = result['to']
                self.content = result['content']
                self.time = result['time']

    def send(self, from_, to, content):
        self.from_ = from_
        self.to = to
        self.content = content
        self._id = self._msg.insert_one(
            {'from': from_, 'to': to, 'content': content, 'time': time.time()})

    @property
    def new(self):
        return (self._id is None)

    def remove(self):
        self._msg.delete_one({'_id': self._id})
        self._id = self.from_ = self.to = self.content = self.time = None

    @classmethod
    def find_to(cls, to):
        return cls._msg.find({'to': to}).sort('time', pymongo.DESCENDING)

    @classmethod
    def num_to(cls, user):
        return cls._msg.find({'to': user}).count()

    @classmethod
    def get_collect(cls):
        return cls._msg

    def __str__(self):
        if self._id is None:
            return 'Message at %s' % id(self)
        return 'Message(%s) from %s to %s: %s...' % (self._id, self.from_,
                                                     self.to, self.content[:50])

    def __repr__(self):
        if self._id is None:
            return 'Message()'
        return 'Message(%s)' % self._id

class Jolla(object):
    _jolla = db.jolla

    # link: source url (Unique)
    # title: source title
    # url: title.replace(' ', '-')(Unique)
    # author: source author
    # content: source content in markdown format
    # headimg
    # trusted_translation: url

    def __init__(self, url=None):
        if url is None:
            self.jolla_info = None
        else:
            self.jolla_info = self.find_url(url)

    def add(self, link, title, author, content, url=None, headimg=None,
            cover=None, trusted_translation=None, index=0):
        if url is None:
            url = self.mkurl(link, author)

        info = {
            'link': link,
            'title': title,
            'author': author,
            'content': content,
            'url': url,
            'headimg': headimg,
            'cover': cover,
            'createtime': time.time(),
            'edittime': time.time(),
            'trusted_translation': trusted_translation,
            'index': index
        }

        self.jolla_info = info
        return self.jolla_info

    def save(self, t=None):
        jolla_info = self.jolla_info
        jolla_info['edittime'] = t or time.time()
        if '_id' in jolla_info:
            self._jolla.replace_one(
                {'_id': jolla_info['id']},
                jolla_info)
            result = jolla_info['_id']
        else:
            result  = self._jolla.insert_one(self.jolla_info)
            jolla_info['_id'] = result
        return result

    def get(self):
        return self.jolla_info

    def set(self, value):
        if self.jolla_info is None:
            self.jolla_info = value
            return
        self.jolla_info.update(value)

    def remove(self):
        self._jolla.delete_one(self.jolla_info)
        self.jolla_info = None

    @property
    def new(self):
        return self.jolla_info is None

    def mkurl(self, link, author):
        splited = link.split('/')
        last = False
        while splited:
            last = splited.pop().strip()
            if last:
                break
        else:
            raise ValueError("Can't make url for %s", link)
        url = last.replace(' ', '-')
        if self.find_url(url) is None:
            logger.debug('url as %s', url)
            return url
        url = '%s-by-%s' % (url, author.replace(' ', '-'))
        if self.find_url(url) is None:
            logger.debug('url as %s', url)
            return url

        idx = 0
        while True:
            idx += 1
            theurl = '%s-%s' % (url, idx)
            logger.debug('searching %s', theurl)
            if self.find_url(theurl) is None:
                logger.debug('url as %s', theurl)
                return theurl

    @classmethod
    def all(cls):
        return cls._jolla.find({}).sort(
            (('index', pymongo.ASCENDING),
             ('createtime', pymongo.DESCENDING)
            ))

    @classmethod
    def find_url(cls, url):
        return cls._jolla.find_one({'url': url})

    @classmethod
    def find_link(cls, link):
        return cls._jolla.find_one({'link': link})

    @classmethod
    def find_id(cls, id):
        return cls._jolla.find_one({'_id': id})


class Article(object):
    _article = db.article
    PUB_LICENSE = 0
    CC_LICENSE = 1

    AWAIT = 0
    TRUSTED = 1
    REJECT = 2
    # title
    # url: title.replace(" ", "-")(Unique)
    # board
    # content
    # license(int)
    # author
    # email
    # show_email: True/False
    # transref: Jolla translation only
    # transref: same as Jolla.url
    # transinfo: Jolla translation only
    # transinfo = {link: , author: , url: , title: ,
    #              headimg:, status:, share:, cover: };
    # same as Jolla.
    # status: AWAIT/TRUSTED/REJECT
    # index: same as Jolla.index(cache)

    # if url exists, then add "-by-"+username
    # if still exists, then add "-1", "-2", etc.

    def __init__(self, url=None):
        if url is None:
            self.article_info = None
        else:
            self.article_info = self.find_url(url)

    def add(self, board, title, content, author, email, url=None,
            show_email=True, license=CC_LICENSE, transinfo=None, index=0):

        if url is None:
            if transinfo is not None:
                url = self.mkurl(transinfo['title'], author)
            else:
                url = self.mkurl(title, author)

        info = {
            'board': board,
            'title': title,
            'url': url,
            'content': content,
            'author': author,
            'email': email,
            'show_email': show_email,
            'license': license,
            'createtime': time.time(),
            'edittime': time.time(),
            'index': index,
        }

        if transinfo is not None:
            info['transinfo'] = transinfo
            info['transref'] = transinfo['url']

        self.article_info = info
        logger.info("New article %s", title)
        return self.article_info

    @classmethod
    def find_url(cls, url):
        return cls._article.find_one({'url': url})

    @classmethod
    def find_ref(cls, ref):
        return cls._article.find({'transref': ref})

    @classmethod
    def find_ref_number(cls, ref):
        return cls._article.find({'transref': ref}).count()

    @classmethod
    def find_ref_of_user(cls, refurl, user):
        return cls._article.find_one({'transref': refurl, 'author': user})

    @classmethod
    def find_ref_of_email(cls, refurl, email):
        return cls._article.find_one({'transref': refurl, 'email': email})

    @classmethod
    def find_trans_url_translator(cls, url, author):
        return cls._article.find_one({'transref': url, 'author': author})

    @classmethod
    def find_by(cls, author):
        return cls._article.find({'author': author})

    def get(self):
        return self.article_info

    def set(self, info):
        if self.article_info is None:
            self.article_info = info
            return
        self.article_info.update(info)

    def save(self):
        info = self.article_info
        coll = self._article
        if '_id' in info:
            coll.replace_one({'_id': info['_id']}, info)
            return info['_id']
        return coll.insert_one(self.article_info)

    @classmethod
    def get_collect(cls):
        return cls._article

    @property
    def new(self):
        return self.article_info is None

    @classmethod
    def mkurl(cls, title, author):
        url = title.replace(' ', '-')
        if cls.find_url(url) is None:
            return url
        url = '%s-by-%s' % (url, author.replace(' ', '-'))
        if cls.find_url(url) is None:
            return url

        idx = 0
        while True:
            idx += 1
            theurl = '%s-%s' % (url, idx)
            if cls.find_url(theurl) is None:
                return theurl

    @classmethod
    def find_jollas(cls):
        return cls._article.find({'board': 'jolla'}).sort(
            (('index', pymongo.ASCENDING),
             ('createtime', pymongo.DESCENDING)
            ))

    @classmethod
    def find_trusted_jollas(cls, skip=0, limit=None):
        result = cls._article.find(
            {'board': 'jolla', 'transinfo.status': cls.TRUSTED}
        ).sort(
            (('index', pymongo.ASCENDING),
             ('createtime', pymongo.DESCENDING)
            )
        )
        if limit is None:
            return result[skip:]
        return result[skip: skip + limit]

    @classmethod
    def find_need_shown(cls, skip=0, limit=None):
        result = cls._article.find({
            '$or': [
                {'transinfo.status': {'$exists': False}},
                {'transinfo.status': cls.TRUSTED}
            ]
        }).sort(
            (('index', pymongo.ASCENDING),
             ('createtime', pymongo.DESCENDING)
            )
        )
        if limit is None:
            return result[skip:]
        return result[skip:skip + limit]

    @classmethod
    def num_by(cls, user):
        return cls._article.find({'author': user}).count()


class JollaAuthor(object):
    _jolla_author = db.jolla_author

    def __init__(self, name):
        result = self.find_author(name)
        if result is None:
            self._info = {'name': name, '_id': None}
        else:
            self._info = result

    @property
    def photo(self):
        return self._info.get('photo', None)
    @photo.setter
    def photo(self, value):
        self._info['photo'] = value

    @property
    def name(self):
        return self._info['name']

    @property
    def description(self):
        return self._info.get('description', None)
    @description.setter
    def description(self, value):
        self._info['description'] = value

    @property
    def translation(self):
        return self._info.get('translation', None)
    @translation.setter
    def translation(self, value):
        self._info['translation'] = value

    @property
    def new(self):
        return self._info['_id'] is None

    def save(self, photo=None, description=None, translation=None):
        info = {
            'name': self.name,
            'photo': photo or self.photo,
            'description': description or self.description,
            'translation': translation or self.translation,
        }

        coll = self._jolla_author
        if self._info['_id'] is not None:
            _id = self._info['_id']
            info['_id'] = _id
            coll.replace_one({'id': _id}, info)
        else:
            _id = coll.insert_one(info)
        self._info.clear()
        self._info.update(info)
        self._info['_id'] = _id

    @classmethod
    def find_author(self, name):
        return self._jolla_author.find_one({'name': name})

    @classmethod
    def all(self):
        return self._jolla_author.find({})

    @classmethod
    def get_collect(self):
        return self._jolla_author

    def remove(self):
        assert not self.new
        self._jolla_author.delete_one(self._info)

    def __str__(self):
        return ('JollaAuthor(name: %s, photo: %s, '
                'description: %.10r..., translation: %.10r)') % (
                    self.name, self.photo, self.description, self.translation)


class Email(object):
    _email = db.email
    _extra = _email.find_one({'name': '_extra'}) or {}

    # name: unique id
    # title
    # content
    # add_main_title: title of the email will be `title` + ' | ' + `main_title`
    # add_footer: add foot for the email
    # attachment: list of filename

    # name: _extra
    # main_title: the value of the main_title, usu. "tomorrow.becomes.today"
    # footer: the value of the footer, usu. basic info/donate info

    def __init__(self, name=None):
        self._info = self._email.find_one({'name': name}) or {}

    def get(self):
        return self._info

    def save(self):
        self._email.insert_one(self._info)

    @property
    def new(self):
        return '_id' not in self._info

    def format(self, use_zh=False):
        data = self._info['default']
        extra = self._extra['default']
        if use_zh:
            if 'zh' in self._info:
                data = self._info['zh']
            if 'zh' in self._extra:
                extra = self._extra['zh']
        if data.get('add_main_title', True):
            data['title'] = '%s | %s' % (data['title'], extra['main_title'])
        if data.get('add_footer', True):
            data['content'] += extra['footer']

        return data

class File(object):
    _file = db.file

    # name: filename
    # type: file type(mime info)
    # user_level: least level

if __name__ == '__main__':
    import docopt
    import os
    import sys
    sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..')))
    from lib.tool.bashlog import stdoutlogger, DEBUG
    sys.path.pop(0)
    stdoutlogger(logger, level=DEBUG)

    args = docopt.docopt(__doc__, help=True)

    if args['--add']:
        u = User(args['--user'])
        assert u.new
        e = args['--email']
        assert e
        p = args['--pwd']
        assert p
        t = args['--type']
        if t is None:
            t = User.normal
        else:
            if t.isdigit():
                t = int(t)
                assert t in (User.admin, User.normal)
            else:
                to_type = {'admin': User.admin, 'normal': User.normal}
                assert t in type(to_type.keys())
                t = to_type[t]
        u.add(email=e, pwd=p, type=t)
        u.save()
        sys.exit()
    if args['--delete']:
        u = User(args['--user'] or args['--email'])
        assert not u.new
        u.remove()
