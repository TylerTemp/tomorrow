import tornado.web
from .base import BaseHandler
from lib.db.tomorrow import Auth, User
import logging

logger = logging.getLogger('tomorrow.oauth2.confirm')

class ConfirmHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, app_key):
        user_name = self.current_user['user']
        logger.debug('get app %s for %s', app_key, user_name)
        auth = self.get_auth(app_key)
        app_name = auth.name

        return self.render(
            'tomorrow/oauth/confirm.html',
            user_name=user_name,
            app_name=app_name
        )

    @tornado.web.authenticated
    def post(self, app_key):
        user_name = self.current_user['user']
        logger.debug('get app %s for %s', app_key, user_name)
        auth = self.get_auth(app_key)
        user = User(user_name)
        user.get().setdefault('app', []).append({'key': app_key})
        user.save()

        if self.is_ajax():
            self.write({'error': 0, 'redirect': auth.callback})

        return self.redirect(auth.callback)

    def get_auth(self, app_key):
        auth = Auth(app_key)
        if not auth:
            raise tornado.web.HTTPError(500, 'App not exists')
        return auth