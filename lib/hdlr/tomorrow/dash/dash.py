import tornado.web
import logging
import os
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

from lib.db.tomorrow import User, Article, Message
from .base import BaseHandler


class DashboardHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.dash.home')

    @tornado.web.authenticated
    def get(self):

        user = self.current_user

        folder_path = self.get_user_path(user.name)
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
            'tomorrow/admin/dash/home.html',
            user=user,
            article_num=Article.by(user.name).count(),
            file_num=file_num,
            img_num=img_num,
            msg_num=0
        )
