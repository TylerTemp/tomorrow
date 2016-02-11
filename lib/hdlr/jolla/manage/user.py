from ..base import BaseHandler
from lib.db.jolla import User

class UserHandler(BaseHandler):

    def get(self):

        return self.render(
            'jolla/manage/user.html',
            users=self.all_users(),
        )

    def all_users(self):
        for each in User.all():
            u = User()
            u.update(each)
            yield u