import tornado.web
import logging
import json
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.config import Config
from lib.db import User
from lib.db import Article
sys.path.pop(0)

logger = logging.getLogger('tomorrow.user')


def its_myself(func):

    def wrapper(self, user):
        userinfo = self.get_current_user()
        urluser = unquote(user)
        if userinfo is None or userinfo['user'] != urluser:
            logger.debug('redirect to %s', urluser)
            return self.redirect('/hi/%s/' % quote(urluser))

        return func(self, user)

    return wrapper


class _Handler(BaseHandler):

    def render(self, template_name, **kwargs):
        user_info = self.get_current_user()
        user_name = user_info['user']
        kwargs['main_url'] = '/am/%s' % quote(user_name)
        if 'user_name' not in kwargs:
            kwargs['user_name'] = user_name

        if 'user_type' not in kwargs:
            kwargs['user_type'] = user_info['type']

        kwargs['NORMAL'] = User.normal
        kwargs['ADMIN'] = User.admin
        kwargs['ROOT'] = User.root

        return super(_Handler, self).render(
            template_name,
            **kwargs
        )


class DashboardHandler(_Handler):

    @its_myself
    @tornado.web.authenticated
    def get(self, user):

        url_user = unquote(user)

        user_info = self.get_current_user()

        user = User(user_info['user'])
        user_info = user.get()
        user_name = user_info['user']

        verify_mail = ('verify' in user_info and
                       user_info['verify']['for'] == user.NEWEMAIL)

        folder_path = self.get_user_path(user_name)
        file_num = len(os.listdir(os.path.join(folder_path, 'file')))
        img_num = len(os.listdir(os.path.join(folder_path, 'img')))

        return self.render(
            'dash/home.html',
            user_email=user_info['email'],
            showe_mail=user_info['show_email'],
            active=user_info['active'],
            verify_mail=verify_mail,
            user_type=user_info['type'],
            user_img=user_info.get('img', None),

            article_num=Article.num_by(user_name),
            file_num=file_num,
            img_num=img_num,
        )

class InfoHandler(_Handler):
    config = Config()

    @its_myself
    @tornado.web.authenticated
    def get(self, user):

        user = User(self.get_current_user()['user'])
        user_info = user.get()
        size_limit = self.config.size_limit[user_info['type']]
        if size_limit != float('inf'):
            size_limit = '%.2f %s' % self.unit_satisfy(size_limit)

        return self.render(
            'dash/info.html',
            user_img=user_info.get('img', None),
            user_email=user_info['email'],
            show_email=user_info['show_email'],
            size_limit=size_limit,
        )

    @tornado.web.authenticated
    def post(self, user):
        userinfo = self.get_current_user()
        urluser = unquote(user)
        if userinfo is None or userinfo['user'] != urluser:
            raise tornado.web.HTTPError(500, 'user %s try to modefy user %s',
                                        userinfo['user'], urluser)

        # this should be bool. But I get string('true'/'false'). WHY?
        show_email = self.get_argument('show_email')
        # set to None if it's empty string
        user_img = self.get_argument('img_url', None) or None
        if show_email not in (True, False):
            logger.info('get show_email (%r) of type (%s)',
                show_email, type(show_email))
            show_email = {'true': True, 'false': False}[show_email]
        logger.debug('show_email: %r; user_img: %r', show_email, user_img)
        user = User(userinfo['user'])
        user_info = user.get()
        user_info.update({'img': user_img, 'show_email': show_email})
        user.save()

        return self.write(json.dumps({'error': 0}))

    @classmethod
    def unit_satisfy(cls, b):
        appropriate_size = b
        appropriate_unit = 'B'
        units = ('B', 'KB', 'MB', 'GB', 'TB')
        index = 0

        while (appropriate_size >> 10) >= 1024 and index < len(units) - 1:
            appropriate_size >>= 10
            index += 1
        return (appropriate_size / 1024, units[index])

class InformationHandler(_Handler):

    pass

if __name__ == '__main__':
    for each in (1, 1024, 1024 ** 2, 1024 ** 3, 1024 ** 4, 1024 ** 5, 1024 ** 6):
        print(InfoHandler.unit_satisfy(each+990))
