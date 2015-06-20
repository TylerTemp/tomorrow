import tornado.web
import logging
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.db import User
from lib.db import Article
from lib.db import Message
from lib.hdlr.dash.base import ItsMyself
from lib.hdlr.dash.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.dash')


class DashboardHandler(BaseHandler):

    @ItsMyself('')
    @tornado.web.authenticated
    def get(self, user):

        url_user = unquote(user)

        user_info = self.current_user

        user = User(user_info['user'])
        user_info = user.get()
        user_name = user_info['user']

        verify_mail = ('verify' in user_info and
                       user_info['verify']['for'] == user.NEWEMAIL)

        folder_path = self.get_user_path(user_name)
        file_path = os.path.join(folder_path, 'file')
        if os.path.exists(file_path):
            file_num = len(os.listdir(file_path))
        else:
            file_num = 0
        img_path = os.path.join(folder_path, 'img')
        if os.path.exists(img_path):
            img_num = len(os.listdir(img_path))
        else:
            img_num = 0

        return self.render(
            'dash/home.html',
            user_email=user_info['email'],
            showe_mail=user_info['show_email'],
            active=user_info['active'],
            verify_mail=verify_mail,
            user_type=user_info['type'],
            user_img=user_info.get('img', None),
            act='home',

            article_num=Article.num_by(user_name),
            file_num=file_num,
            img_num=img_num,
            msg_num=Message.num_to(user_name)
        )
