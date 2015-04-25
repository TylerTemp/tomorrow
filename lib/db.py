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
from passlib.hash import sha256_crypt

logger = logging.getLogger('db')

client = pymongo.MongoClient()
db = client['tomorrow']


class User(object):
    _user = db.user

    block = 0
    normal = 1
    admin = 2
    root = 3

    # user
    # email
    # pwd
    # nickname
    # type
    def __init__(self, user_or_email):
        self.user_info = self.find_user(user_or_email)
        self.new = (self.user_info is None)
        if self.new:
            self.user = user_or_email if '@' not in user_or_email else None
            self.email = user_or_email if '@' in user_or_email else None
        else:
            self.user = self.user_info['user']
            self.email = self.user_info['email']

    def add(self, user=None, email=None, pwd=None, show_email=False, type=None):
        assert pwd
        pwd = sha256_crypt.encrypt(pwd)
        user = user or self.user
        email = email or self.email
        assert user and email
        logger.info('new user %s', user)
        type = self.normal if type is None else type
        self.user_info = {
            'user': user,
            'email': email,
            'pwd': pwd,
            'show_email': show_email,
            'type': type,
        }
        self.user_info['_id'] = self.save()
        self.new = False
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
        self.new = True
        self.user_info = None

    def save(self):
        return self._user.save(self.user_info)

    def get(self):
        return self.user_info

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


class Article(object):
    _article = db.article
    board = {'jolla'}
    board.update(Board.all())

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
