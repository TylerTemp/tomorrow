import logging
import json
import re
from passlib.hash import sha256_crypt
from bson.objectid import ObjectId

try:
    from urllib.parse import quote
except ImportError:
    from urlparse import quote

import sys
import os
sys.path.insert(0, os.path.normpath(
                    os.path.join(__file__, '..', '..', '..', '..')))
from lib.hdlr.dash.base import BaseHandler, ItsMyself
from lib.hdlr.base import EnsureUser, EnsureSsl
from lib.db import User, Message, Article, Jolla
from lib.tool.mail import Email
from lib.tool.tracemore import get_exc_plus
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.manage.jolla.post')

class UserHandler(BaseHandler):
    ERROR_USER_NOT_FOUND = 1
    ERROR_USER_EXIST = 2
    ERROR_EMAIL_EXIST = 4
    EMAIL_RE = re.compile(r'^[\w\d.+-]+@([\w\d.]+\.)+\w{2,}$')
    USER_RE = re.compile(
        r'^[a-zA-Z0-9\u4e00-\u9fa5_\ \-][a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]'
        r'|[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-][a-zA-Z0-9\u4e00-\u9fa5_\ \-]'
        r'|[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]{3,100}$')

    @ItsMyself('manage/user/')
    @EnsureUser(level=User.root, active=True)
    @EnsureSsl(permanent=True)
    def get(self, user=None):
        return self.render(
            'dash/manage/user.html',
            all_users=User.all(),
            ADMIN=User.admin,
            ROOT=User.root,
            act=('manage', 'manage-user')
        )

    @ItsMyself('manage/user/')
    @EnsureUser(level=User.root, active=True)
    @EnsureSsl(permanent=True)
    def post(self, user=None):
        self.check_xsrf_cookie()

        action = self.get_argument('action', None)
        flag = 0

        if action == 'delete':
            self.delete_user()

        user = User.init_by_id(self.get_argument('id', None))
        if user.new and action != 'invite':
            return self.write(json.dumps({'error': self.ERROR_USER_NOT_FOUND}))

        user_info = user.get() or {
            'user': None,
            'email': None,
            'pwd': None,
            'show_email': False,
            'type': User.normal,
            'active': False
        }
        old_user_info = dict(user_info)

        new_user_name = self.get_argument('user', None) or None
        old_user_name = user_info['user']
        if new_user_name is not None:
            assert self.USER_RE.match(new_user_name) is not None
            if (new_user_name != old_user_name
                    and not User(new_user_name).new):
                flag |= self.ERROR_USER_EXIST

        new_email = self.get_argument('email') or None
        old_email = user_info['email']
        if new_email is not None:
            assert self.EMAIL_RE.match(new_email) is not None
            if (new_email != old_email and not User(new_email).new):
                flag |= self.ERROR_EMAIL_EXIST

        if flag != 0:
            return self.write(json.dumps({'error': flag}))

        if not new_user_name:
            self.set_code(user_info, User.CHANGEUSER)
        else:
            user_info['user'] = new_user_name

        if not new_email:
            self.set_code(user_info, User.CHANGEEMAIL)
        else:
            user_info['email'] = new_email

        user_info['type'] = int(self.get_argument('group', 0))
        user_info['active'] = self.get_argument('active', False)
        user_info['show_email'] = self.get_argument('show_email', False)
        lang = self.get_argument('lang', None)
        if lang is not None and lang.lower() == 'none':
            lang = None
        self.set_or_remove(user_info, 'lang', lang)
        service = []
        if self.get_argument('ss', False):
            service.append('ss')
        self.set_or_remove(user_info, 'service', service)

        self.set_or_remove(user_info,
                           'img',
                           self.get_argument('avatar', False))
        change_pwd = self.get_argument('change_pwd', False)
        if action == 'invite' or change_pwd:
            pwd = self.get_argument('pwd', None)
            if pwd:
                pwd = sha256_crypt.encrypt(pwd)
            user_info['pwd'] = pwd

        if action == 'invite':
            User.get_collect().insert_one(user_info)
        else:
            user.save()
        info = dict(user_info)
        info.pop('_id')
        info['group'] = int(info.pop('type'))
        info['error'] = 0
        info['avatar'] = info.get('img', None)
        if info['pwd']:
            info['pwd'] = '********'
        self.write(json.dumps(info))
        self.finish()

        if None not in (old_user_name, new_user_name):
            Article.get_collect().update_many(
                {'author': old_user_name}, {'$set': {'author': new_user_name}})
            Message.get_collect().update_many(
                {'from': old_user_name}, {'$set': {'from': new_user_name}}
            )
            Message.get_collect().update_many(
                {'to': old_user_name}, {'$set': {'to': new_user_name}}
            )

        if None not in (old_email, new_email):
            Article.get_collect().update_many(
                {'email': old_email}, {'$set': {'email': new_email}}
            )

        send_mail_to = filter(lambda x: x, (old_email, new_email))
        language = lang or 'en'
        for send_to in send_mail_to:
            mail_man = Email(send_to, language)
            if action == 'invite':
                kwargs = {'invitor': self.current_user['user']}
                if 'verify' in user_info:
                    name = 'invite'
                    code = user_info['verify']['code']
                    kwargs.update({'code': code, 'escaped_code': quote(code)})
                else:
                    name = 'invite_no_verify'
                try:
                    mail_man.send('invite', **kwargs)
                except BaseException as e:
                    logger.error(get_exc_plus())

    def delete_user(self):
        msg_coll = Message.get_collect()
        article_coll = Article.get_collect()
        user = User.init_by_id(self.get_argument('id'))
        if user.new:
            return self.write(json.dumps({'error': flag}))
        else:
            logger.warning('delete user %s', user)
            user.remove()
            self.write(json.dumps({'error': 0}))
            self.finish()

            user_name = user.get()['user']
            msg_coll.delete_many({'to': user_name})

            for each_article in article_coll.find({
                    'author': user_name,
                    'status': Article.TRUSTED}):
                jolla_url = each_article['transref']
                jolla = Jolla(jolla_url)
                assert not jolla.new
                jolla.get()['trusted_translation'] = None
                jolla.save()
            article_coll.delete_many({'author': user_name})

    def set_or_remove(self, info, name, value):
        if value:
            info[name] = value
        else:
            if name in info:
                info.pop(name)

    def set_code(self, user_info, for_):
        verify = user_info.setdefault('verify', {})
        if verify:
            orl_for = verify['for']
            code = verify['code']
        else:
            orl_for = 0
            code = User.generate()
        verify.clear()
        verify.update({'for': orl_for | for_, 'code': code})
