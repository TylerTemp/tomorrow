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

logger = logging.getLogger('tomorrow.db')

client = pymongo.MongoClient()
db = client['tomorrow']


class User(object):
    _user = db.user

    normal = 0
    admin = 1
    root = 2

    NEWEMAIL = 0
    CHANGEEMAIL = 1
    CHANGEPWD = 2
    CHANGEUSER = 3

    OK = 0
    ERROR_NOT_APPLY = 1
    ERROR_WRONG = 2
    ERROR_OUT_OF_TIME = 3

    # user
    # email
    # pwd
    # nickname
    # type
    def __init__(self, user_or_email):
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
        assert not self.new
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
        self._user.delete_one(self.user_info)
        # self._user.remove({'user': self.user})
        self.user_info = None

    def set_img(self, url):
        self.user_info['img'] = url

    def save(self):
        result = self._user.save(self.user_info)
        self.user_info['_id'] = result
        return result

    def get(self):
        return self.user_info

    def set_code(self, for_, code, expire=None):
        info = self.user_info
        assert info
        info['verify'] = {
            'for': for_,
            'code': code
        }
        if expire is not None:
            info['verify']['expire'] = expire

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


class Board(object):
    _board = db.board

    @classmethod
    def all(self):
        return self._board.find({})


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
            trusted_translation=None):
        if url is None:
            url = self.mkurl(title, author)

        info = {
            'link': link,
            'title': title,
            'author': author,
            'content': content,
            'url': url,
            'headimg': headimg,
            'createtime': time.time(),
            'edittime': time.time(),
            'trusted_translation': trusted_translation,
        }

        self.jolla_info = info
        return self.jolla_info

    def save(self, t=None):
        self.jolla_info['edittime'] = t or time.time()
        result  = self._jolla.save(self.jolla_info)
        self.jolla_info['_id'] = result
        return result

    def get(self):
        return self.jolla_info

    @property
    def new(self):
        return self.jolla_info is None

    def mkurl(self, title, author):
        url = title.replace(' ', '-')
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

    # todo: order by time/...
    @classmethod
    def all(cls):
        return cls._jolla.find({})

    @classmethod
    def find_url(cls, url):
        return cls._jolla.find_one({'url': url})

    @classmethod
    def find_link(cls, link):
        return cls._jolla.find_one({'link': link})


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
    #              headimg:, status:, reprint: };
    # same as Jolla. status: AWAIT/TRUSTED/REJECT

    # if url exists, then add "-by-"+username
    # if still exists, then add "-1", "-2", etc.

    def __init__(self, url=None):
        if url is None:
            self.article_info = None
        else:
            self.article_info = self.find_url(url)

    def add(self, board, title, content, author, email, url=None,
            show_email=True, license=CC_LICENSE, transinfo=None):

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
        self.article_info = info

    def save(self):
        return self._article.save(self.article_info)

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
        return cls._article.find({'board': 'jolla'})

    @classmethod
    def num_by(cls, user):
        return cls._article.find({'author': user}).count()


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
        sys.exit()
    if args['--delete']:
        u = User(args['--user'] or args['--email'])
        assert not u.new
        u.remove()
