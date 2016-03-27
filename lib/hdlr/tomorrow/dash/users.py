from bson import ObjectId
from lib.db.tomorrow import User
from .base import BaseHandler
from ..base import EnsureUser


class UsersHandler(BaseHandler):

    @EnsureUser(level=User.ROOT)
    def get(self):
        self.xsrf_token
        return self.render(
            'tomorrow/dash/users.html',
            users=User.find({})
        )

    @EnsureUser(level=User.ROOT)
    def post(self):
        self.check_xsrf_cookie()

        user = User.find_one({'_id': ObjectId(self.get_argument('_id'))})
        assert user, '%s not exists' % self.get_argument('_id')

        user.name = self.get_argument('name', '') or None
        user.email = self.get_argument('email', '') or None

        if self.get_argument('change-pwd', False):
            user.pwd = self.get_argument('pwd')

        mask = self.get_argument('for', '') or None
        if mask:
            user.verify['for'] = mask
            user.verify['code'] = self.get_argument('code')
            assert user.verify['code']
            expire = user.get_argument('expire', '') or None
            if expire:
                user.verify['expire'] = expire
        else:
            del user.verify

        user.active = bool(self.get_argument('actived', False))

        ss = self.get_argument('ss', False)
        if ss:
            if ss not in user.service:
                user.service.append('ss')
        else:
            if ss in user.service:
                user.service.remove('ss')

        user.save()

        return self.write({'error': 0})
