# todo: asynchronization

import pymongo
import logging
from passlib.hash import sha256_crypt

logger = logging.getLogger('db')

client = pymongo.MongoClient()
db = client['tomorrow']


class User(object):
    _user = db.user
    admin = 0
    normal = 1

    # user
    # email
    # pwd
    # nickname
    # type
    def __init__(self, user):
        self.user_info = self.find_user(user)
        self.new = (self.user_info is None)
        if self.new:
            self.user = user
        else:
            self.user = self.user_info['user']

    def add(self, **kwd):
        logger.info('new user %s', self.user)
        kwd['pwd'] = sha256_crypt.encrypt(kwd['pwd'])
        kwd['user'] = self.user
        self.user_info = kwd
        self.user_info['_id'] = self.save()
        self.new = False
        return self.user_info

    @classmethod
    def find_user(cls, user):
        return cls._user.find_one({'user': user})

    def remove(self):
        logger.info('remove user %s', self.user_info)
        self._user.remove(self.user_info)
        # self._user.remove({'user': self.user})
        self.new = True
        self.user_info = {}

    def save(self):
        return self._user.save(self.user_info)

    def __str__(self):
        if self.new:
            return 'new User(%s)' % self.user
        return str(self.user_info)

    def __repr__(self):
        if self.new:
            return 'User(%s)' % self.user
        return repr(self.user_info)


class Article(object):
    _article = db.article
    board = ('jolla', 'blog')

    def __init__(self, title=None):
        self.article_info = self.find_user(user)
        self.new = (self.article_info is None)
        if self.new:
            self.title = user
        else:
            self.title = self.user_info['user']

    def add(self, **kwd):
        assert kwd['board'] in self.board
        logger.info('new article %s', self.title)
        kwd['title'] = self.title
        self.article_info = kwd
        self.article_info['_id'] = self.save()
        self.new = False
        return self.user_info

    @classmethod
    def find_title(cls, title):
        return cls._article.find_one({'title': titile})

    def save(self):
        return self._article.save(self.article_info)


if __name__ == '__main__':

    import os
    import sys
    sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..')))
    from lib.tool.bashlog import stdoutlogger, DEBUG
    sys.path.pop(0)
    stdoutlogger(logger, level=DEBUG)

    user = User('tylertemp')
    print(user.add('tylertempdev@gmail.com', 'password',
          user.admin, 'TylerTemp'))
    print(user)
    print(user.remove())
    print(user)
    print(User('tylertemp'))
