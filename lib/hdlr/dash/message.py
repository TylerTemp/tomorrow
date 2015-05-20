import tornado.web
import logging
import json
import pymongo
import time
from bson.objectid import ObjectId
import bleach
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.db import Message
from lib.db import User
from lib.tool.md import escape
from lib.hdlr.dash.base import ItsMyself
from lib.hdlr.dash.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.message')


class MessageHandler(BaseHandler):
    ERROR_SEND_TO_SELF = 1
    ERROR_SEND_TO_WHO = 2

    @tornado.web.authenticated
    @ItsMyself('message/')
    def get(self, user):

        self.xsrf_token

        return self.render(
            'dash/message.html',
            msg=self.msgs(self.current_user['user'])
        )

    def msgs(self, user):
        result = Message.find_to(user)
        for each in result:
            each['time_attr'] = time.strftime('%Y-%m-%dT%H:%M:%S',
                                              time.localtime(each['time']))
            each['time_read'] = self.format_time_read(each['time'])
            if each['from'] is None or '@' in each['from']:
                each['url'] = None
                each['avatar'] = None
            else:
                from_user = User(each['from'])
                if from_user.new:
                    each['avatar'] = None
                else:
                    each['avatar'] = from_user.get().get('img', None)
                each['url'] = '/hi/%s/message/' % quote(each['from'])

            each['id'] = str(each['_id'])

            yield each

    def format_time_read(self, t):
        if self.locale.code.startswith('en'):
            return time.ctime(t)
        return time.strftime('%m月%d日，%H:%M', time.localtime(t))

    @tornado.web.authenticated
    @ItsMyself('message/')
    def post(self, user):

        self.check_xsrf_cookie()

        if self.get_argument('action') == 'delete':
            self.delete_msg()
        else:
            self.send_msg()

    def delete_msg(self):
        _id = ObjectId(self.get_argument('id'))

        msg = Message(_id)
        user_name = self.current_user['user']
        user_type = self.current_user['type']

        if user_name != msg.to and user_type <= User.admin:
            raise tornado.web.HTTPError(
                403,
                '%s want to delete %s sent to %s' % (user_name, _id, msg.to))

        msg.remove()

        self.write(json.dumps({'error': 0}))
        self.finish()

    def send_msg(self):
        from_ = self.current_user['user']
        to = self.get_argument('user', None) or None
        content = self.get_argument('msg')

        user_type = self.current_user['type']

        if not content:
            raise tornado.web.HTTPError(
                500,
                '%s want to send an empty content to %s' % (from_, to))

        if from_ == to:
            return self.write(json.dumps({'error': self.ERROR_SEND_TO_SELF}))

        if to:
            to_user = User(to)
            if to_user.new:
                return self.write(json.dumps({'error': self.ERROR_SEND_TO_WHO}))
            to = to_user.get()['user']

        if user_type < User.admin:
            content = '<p>%s</p>' % bleach.bleach(
                content, tags=()).replace('\n', '<br>')


        Message().send(from_, to, content)

        return self.write(json.dumps({'error': 0}))
