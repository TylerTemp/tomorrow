from .base import BaseHandler

class LoginHandler(BaseHandler):

    def get(self):
        url = ('//tomorrow.fake.today/oauth2/authorize/'
               '?client_id=id&redirect_uri=callback')
        return self.render(
            'jolla/login.html',
            tomorrow_url=url,
        )