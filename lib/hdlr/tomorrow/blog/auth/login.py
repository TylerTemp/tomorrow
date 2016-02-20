import logging
from .base import BaseHandler
from lib.db.tomorrow import User
from lib.tool import url


class LoginHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.auth.login')

    def get(self):
        return self.render(
            'tomorrow/blog/auth/login.html',
            user=self.get_argument('user', None),
            query=url.get_query(self.request.uri)
        )

    def post(self):
        self.check_xsrf_cookie()
        user_or_email = self.get_argument('user-or-email')
        user = User(user_or_email)
        if not user:
            self.set_status(403, 'User %r not exists' % user_or_email)
            return self.write({
                'error': 1,
                'message': 'User %r not exists' % user_or_email
            })

        if not user.check_pwd(self.get_argument('pwd')):
            self.set_status(403, 'Password incorrect')
            return self.write({
                'error': 2,
                'message': 'Password incorrect'
            })

        self.login(user, not self.get_argument('remember', False))

        return self.write({
            'error': 0,
            'next': self.get_argument('next', None)
        })
