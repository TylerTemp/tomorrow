# coding: utf-8
import logging
import json
import time
import datetime
import bson
from bson.objectid import ObjectId
try:
    from urllib.parse import quote
except ImportError:
    from urlparse import quote

from lib.hdlr.base import EnsureUser
from lib.db import User, Message
from lib.tool.minsix import py2
from lib.tool.mail import Email
from lib.tool.md import md2html
from ..base import BaseHandler

logger = logging.getLogger('tomorrow.dash.manage.message')


class MessageHandler(BaseHandler):
    ERROR_RECEIVER_NOT_EXIST = 1
    ERROR_RECEIVER_NAME_EMPTY = 2
    ERROR_RECEIVER_EMAIL_EMPTY = 4
    ERROR_SEND_EMAIL_FAILED = 8

    ERROR_SENDER_NOT_EXIST = 16
    ERROR_MSG_NOT_EXIST = 32
    ERROR_TIME_FORMAT = 64
    ERROR_DATE_FORMAT = 128

    @EnsureUser(level=User.root, active=True)
    def get(self, user=None):
        self.xsrf_token
        name = self.get_argument('name', None)
        if name:
            return self.get_user_msg(name)
        return self.render(
            'tomorrow/admin/dash/manage/message.html',
            receive=self.received_msg(None),
            sent=self.sent_msg(None),
            all_users=list(User.all()),
            quote=quote
        )

    @EnsureUser(level=User.root, active=True)
    def post(self, user=None):
        self.check_xsrf_cookie()

        action = self.get_argument('action', None)
        logger.debug(action)
        if action == 'send':
            return self.send()
        elif action == 'delete':
            return self.delete()
        else:    # modify
            return self.modify()

    def send(self):
        from_ = self.get_argument('send-by')
        logger.debug(self.request.arguments)
        tos = self.request.arguments.get('send-to[]', ())
        assert tos, "Can't send to nobody"
        methods = self.request.arguments.get('method[]', ())
        title = self.get_argument('title', None)
        content = self.get_argument('content')
        if not py2:
            tos = tuple(each.decode('utf-8') for each in tos)
            methods = tuple(each.decode('utf-8') for each in methods)

        result = {'<error>': 0,
                  'msg': ('msg' in methods),
                  'email': ('email' in methods)}
        if from_.lower() == '.':
            from_ = None
            sender_name = None
        else:
            user = User.init_by_id(from_)
            if user.new:
                result['<error>'] = self.ERROR_SENDER_NOT_EXIST
                return self.write(json.dumps(result))
            sender_info = user.get()
            sender_name = sender_info['user']

        for send_to in tos:
            this_result = {'error': 0}
            if send_to.lower() == '.':
                is_admin = True
                user_name = None
                user_email = None
                this_result['name'] = 'Administor'
                this_result['email'] = None
                title = title.format(user='Administor')
                content = content.format(user='Administor')
            else:
                is_admin = False
                user = User.init_by_id(send_to)
                if user.new:
                    this_result = {'error': self.ERROR_RECEIVER_NOT_EXIST}
                    result[send_to] = this_result
                    logger.error("user id %s does't exist", send_to)
                    continue
                user_info = user.get()
                user_name = user_info['user']
                user_email = user_info['email']
                this_result['name'] = user_name
                this_result['email'] = user_email
                title = title.format(user=user_name or 'Anonymous User')
                content = content.format(user=user_name or 'Anonymous User')

            if 'msg' in methods:
                if title and title.strip():
                    content = '# %s\n\n%s' % (title, content)
                if not user_name and not is_admin:
                    logger.error('user %s does not have name yet',
                                 user_email or send_to)
                    this_result['error'] |= self.ERROR_RECEIVER_NAME_EMPTY
                else:
                    this_result['from'] = sender_name
                    Message().send(sender_name,
                                   user_name,
                                   content.format(user=user_name))

            if 'email' in methods:
                if not user_email:
                    logger.error('user %s does not have email', sender_name)
                    this_result['error'] |= self.ERROR_RECEIVER_EMAIL_EMPTY
                else:
                    mail_man = Email(user_email, self.locale.code)
                    try:
                        mail_man.send_manually(
                            title or 'Notification | tomorrow.becomes.today',
                            content)
                    except BaseException as e:
                        logger.error(
                            'failed to send mail to %s: %s', user_email, e)
                        this_result['error'] |= \
                            self.ERROR_SEND_EMAIL_FAILED
            result[send_to] = this_result

        return self.write(json.dumps(result))

    def delete(self):
        _id = self.get_argument('id')
        logger.debug('remove msg id %s', _id)
        flag = 0
        try:
            _id = ObjectId(_id)
        except bson.errors.InvalidId:
            flag = self.ERROR_MSG_NOT_EXIST
        else:
            msg = Message(_id)
            if msg.new:
                flag = self.ERROR_MSG_NOT_EXIST

        if flag != 0:
            self.clear()
            self.set_status(403)
            return self.write(json.dumps({'error': self.ERROR_MSG_NOT_EXIST}))

        msg.remove()
        return self.write(json.dumps({'error': 0}))

    def modify(self):
        _id = self.get_argument('id')
        to = self.get_argument('send-to', None) or None
        from_ = self.get_argument('send-by', None) or None
        deleted = self.get_argument('sender-deleted', False)
        receiver_status = int(self.get_argument('receiver-status'))
        content = self.get_argument('content')
        assert content
        flag = 0
        try:
            _id = ObjectId(_id)
        except bson.errors.InvalidId:
            flag = self.ERROR_MSG_NOT_EXIST
        else:
            msg = Message(_id)
            if msg.new:
                flag = self.ERROR_MSG_NOT_EXIST

        if flag == 0:
            if from_ and '@' not in from_:
                user = User(from_)
                if user.new:
                    flag |= self.ERROR_SENDER_NOT_EXIST
                else:
                    from_ = user.get()['user']
            if to:
                user = User(to)
                if user.new:
                    flag |= self.ERROR_RECEIVER_NOT_EXIST
                else:
                    to = user.get()['user']

        if flag == 0:
            now_obj = time.gmtime()
            sent_time = self.get_argument('time', None)
            if sent_time is not None:
                try:
                    time_obj = time.strptime(sent_time, '%H:%M:%S')
                except ValueError:
                    flag |= self.ERROR_TIME_FORMAT
                    time_obj = None
            else:
                time_obj = now_obj

            if time_obj is not None:
                hour = time_obj.tm_hour
                minute = time_obj.tm_min
                second = time_obj.tm_sec

            sent_date = self.get_argument('date', None)
            if sent_date is not None:
                try:
                    date_obj = time.strptime(sent_date, '%m/%d/%y')
                except ValueError:
                    flag |= self.ERROR_DATE_FORMAT
                    date_obj = None
            else:
                date_obj = now_obj

            if date_obj is not None:
                year = date_obj.tm_year
                month = date_obj.tm_mon
                day = date_obj.tm_mday

        result = {'error': flag}
        if flag == 0:
            time_stamp = datetime.datetime(
                year, month, day, hour, minute, second).timestamp()
            msg.from_ = from_
            msg.to = to
            msg.content = content
            msg.sender_delete = deleted
            msg.receiver_status = receiver_status
            msg.time = time_stamp
            msg.save()
            info = {
                'from': msg.from_,
                'to': msg.to,
                'content': msg.content,
                'sender_delete': msg.sender_delete,
                'receiver_status': msg.receiver_status,
                'time': msg.time,
                '_id': str(msg._id)
            }
            self.format_msg(info)
            _xsrf = self.xsrf_token
            if not py2:
                _xsrf = _xsrf.decode('utf-8')
            info['_xsrf'] = _xsrf
            result.update(info)
        else:
            self.clear()
            self.set_status(403)
        return self.write(json.dumps(result))

    def received_msg(self, name):
        for each in Message.find_to(name):
            self.format_msg(each)
            yield each

    def sent_msg(self, name):
        for each in Message.find_from(name):
            self.format_msg(each)
            yield each

    def format_msg(self, info):
        from_user = info['from']
        if from_user is None:
            from_avatar = None
            from_email = None
        elif '@' in from_user:
            from_avatar = None
            from_email = from_user
        else:
            user_info = User(from_user).get()
            from_avatar = user_info.get('img', None)
            from_email = user_info['email']

        info['from_avatar'] = from_avatar
        info['from_email'] = from_email

        to_user = info['to']
        if to_user is None:
            to_avatar = None
            to_email = None
        else:
            user_info = User(to_user).get()
            to_avatar = user_info.get('img', None)
            to_email = user_info['email']

        info['to_avatar'] = to_avatar
        info['to_email'] = to_email
        info['time_attr'], info['time_read'], \
                info['date_read'], info['time_pick']= \
            self.format_time(info['time'])
        info['html_content'] = md2html(info['content'])

    def format_time(self, t):
        time_obj = time.localtime(t)
        time_attr = time.strftime('%Y-%m-%dT%H:%M:%S', time_obj)
        date = time.strftime('%x', time_obj)
        time_ = time.strftime('%X', time_obj)
        if not self.locale.code.startswith('zh'):
            return time_attr, time.ctime(t), date, time_
        return (time_attr, time.strftime('%m月%d日，%H:%M', time_obj),
                date, time_)

    def get_user_msg(self, user_name):
        if user_name == '.':
            user_name = None
        logger.debug(user_name)
        received = []
        _xsrf = self.xsrf_token
        if not py2:
            _xsrf = _xsrf.decode('utf-8')
        for each in self.received_msg(user_name):
            each['_id'] = str(each['_id'])
            # each.pop('_id')
            each['_xsrf'] = _xsrf
            received.append(each)
        sent = []
        for each in self.sent_msg(user_name):
            each['_id'] = str(each['_id'])
            # each.pop('_id')
            each['_xsrf'] = _xsrf
            sent.append(each)
        return self.write(json.dumps({'name': user_name or '.',
                                      'receive': received,
                                      'sent': sent}))
