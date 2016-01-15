import logging
import json
import tornado.web
import tornado.httpclient
import tornado.gen
from bson import ObjectId
from .base import BaseHandler
from lib.config import Config
from lib.tool.minsix import py3
from lib.db.jolla import User

try:
    from urllib.parse import urlencode
except ImportError:
    from urlparse import urlencode

logger = logging.getLogger('jolla.oauth')

class OAuthHandler(BaseHandler):
    config = Config()

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        code = self.get_argument('code')
        logger.debug(code)
        key = self.tomorrow_key
        secret = self.tomorrow_secret

        client = tornado.httpclient.AsyncHTTPClient()

        config = self.config
        app = config.jolla_app
        token_url = app['token_url']
        args = {'key': key, 'secret': secret, 'code': code}

        logger.info('fetch %s - %s', token_url, args)
        response = yield tornado.gen.Task(client.fetch,
                                          token_url,
                                          method='POST',
                                          body=urlencode(args),
                                          validate_cert=False,
                                          headers={'X-Requested-With':
                                                       'XMLHttpRequest'})
        assert response.code < 500, ('Unexpected result %s(%s)' %
                                     (response.code, response.body))
        body = response.body
        if py3:
            body = body.decode('utf-8')
        result = json.loads(body)
        logger.debug(result)
        uname = result.pop('name', None)
        source = User.TOMORROW
        uid = result['uid']

        user = User.by_source_id(source, ObjectId(uid))
        if user and user.name:
            pass
        else:
            user.name = uname
            user.save()

        self.login(str(user._id), result['token'], result['expire_at'])
        self.redirect('//' + self.config.jolla_host)
