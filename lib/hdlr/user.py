import tornado.web
import logging
import json
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.user')


class UserHandler(BaseHandler):

    def get(self, user):

        user = unquote(user)

        userinfo = self.get_current_user()

        if userinfo is None or user.lower() != userinfo['user'].lower():
            # show person's information
            logger.debug('show info for %s', userinfo)
            return self.show_info(user)

        user = User(userinfo['user'])
        userinfo = user.get()

        verify_mail = ('verify' in userinfo and
                       userinfo['verify']['for'] == user.NEWEMAIL)

        return self.render(
            'hi.html',
            user=userinfo['user'],
            active=userinfo['active'],
            verify_mail=verify_mail,
            usertype = self.user_type(userinfo['type']),
        )

    def show_info(self, user):
        assert False

    def user_type(self, tp):
        if tp == User.normal:
            return self.locale.translate('Registered User')
        if tp == User.admin:
            return self.locale.translate('Administor')
        if tp == User.root:
            return self.locale.translate('Super User')
