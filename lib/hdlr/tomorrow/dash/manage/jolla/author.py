import logging
import json
from bson.objectid import ObjectId
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

from lib.hdlr.base import EnsureUser
from lib.db import JollaAuthor, User, Jolla
from ...base import BaseHandler

logger = logging.getLogger('tomorrow.dash.manage.jolla.post')

class AuthorHandler(BaseHandler):

    @EnsureUser(level=User.admin, active=True)
    def get(self, _=None):
        name = self.get_argument('name', None)
        if name:
            return self.get_info(name)

        self.xsrf_token
        return self.render(
            'tomorrow/admin/dash/manage/jolla/author.html',
            author_and_status=self.get_all_author()
        )

    @ItsMyself('manage/jolla/author/')
    @EnsureUser(level=User.admin, active=True)
    def post(self, _=None):
        self.check_xsrf_cookie()
        name = self.get_argument('name')
        author = JollaAuthor(name)
        if self.get_argument('action', None) == 'delete':
            author.remove()
            logger.info('delete author %s', name)
            return self.write(json.dumps({'error': 0, 'name': name}))
        author.photo = self.get_argument('photo', '').strip() or None
        author.description = self.get_argument('description', '').strip() or None
        author.translation = self.get_argument('translation', '').strip() or None
        author.save()
        return self.write(json.dumps({
            'error': 0,
            'name': author.name,
            'photo': author.photo,
            'description': author.description,
            'translation': author.translation
        }))


    def get_info(self, name):
        author = JollaAuthor(name)
        _id = author.id
        if _id is None:
            _id = ObjectId()
        self.write(json.dumps({
            'name': author.name,
            'photo': author.photo,
            'description': author.description,
            'translation': author.translation,
            'id': str(_id)
        }))

    def get_all_author(self):
        got = set()
        for each in JollaAuthor.all():
            name = each['name']
            got.add(name)
            yield name, each['_id'], (each['photo'] and each['translation'])
        for each in Jolla.all():
            name = each['author']
            if name in got:
                continue
            got.add(name)
            yield name, ObjectId(), False
