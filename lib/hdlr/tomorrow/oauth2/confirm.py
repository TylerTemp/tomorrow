import tornado.web
from .base import BaseHandler
from lib.db.tomorrow import Auth, User
import logging


class ConfirmHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.oauth2.confirm')

    @tornado.web.authenticated
    def get(self, app_key, temp_code=None):
        user = self.current_user
        self.debug('get app %s for %s', app_key, user)
        auth = self.get_auth(app_key)
        app_name = auth.name

        return self.render(
            'tomorrow/oauth/confirm.html',
            user=user,
            app_name=app_name
        )

    @tornado.web.authenticated
    def post(self, app_key, temp_code=None):
        user = self.current_user
        self.debug('get app %s for %s', app_key, user)
        auth = self.get_auth(app_key)
        user.app.append({'key': app_key})
        user.save()

        redirect = self.parse_callback(auth.callback, temp_code)

        if self.is_ajax():
            self.write({'error': 0, 'redirect': redirect})

        self.redirect(redirect)

    def get_auth(self, app_key):
        auth = Auth(app_key)
        if not auth:
            raise tornado.web.HTTPError(500, 'App not exists')
        return auth