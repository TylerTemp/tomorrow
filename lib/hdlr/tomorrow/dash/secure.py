# coding: utf-8
import tornado.web
import logging
import json
import time
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

from lib.db.tomorrow import User, Message
from lib.tool.mail import Email
from lib.tool.tracemore import get_exc_plus
from .base import ItsMyself, BaseHandler

logger = logging.getLogger('tomorrow.dash.secure')

# todo: fix this so it can work again
class SecureHandler(BaseHandler):

    ERROR_FAILED_SEND_EMAIL = 1
    ERROR_NOTHING_TO_SEND = 2

    @tornado.web.authenticated
    @ItsMyself('secure/')
    def get(self, user):

        self.xsrf_token

        user = User(self.current_user['user'])
        user_info = user.get()
        verify_mail = ('verify' in user_info and
                       user_info['verify']['for'] & user.NEWUSER)

        return self.render(
            'tomorrow/admin/dash/secure.html',
            verify_mail=verify_mail,
            user_email=user_info['email'],
            active=user_info['active'],
        )

    @tornado.web.authenticated
    @ItsMyself('secure/')
    # @tornado.web.asynchronous
    # @tornado.gen.engine
    def post(self, user):

        userinfo = self.current_user
        urluser = unquote(user)
        if userinfo['user'] != urluser:
            raise tornado.web.HTTPError(500, 'user %s try to modefy user %s',
                                        userinfo['user'], urluser)

        action = self.get_argument('action', None)  # resend/verify_email/None
        flag = 0
        user = User(userinfo['user'])
        user_info = user.get()
        if action == 'resend':
            if 'verify' not in user_info or user_info['verify']['for'] == 0:
                self.write(json.dumps({'error': self.ERROR_NOTHING_TO_SEND}))
                self.finish()
                return
            expire = user_info['verify'].get('expire', None)
            email = user_info['email']
            code = user_info['verify']['code']
            for_ = user_info['verify']['for']
        elif action == 'verify_email':
            assert user_info['verify']['for'] & user.NEWUSER
            email = self.get_argument('email')
            expire = None
            code = user_info['verify']['code']
            for_ = user_info['verify']['for']
        else:
            if ('verify' in user_info):
                 assert not user_info['verify']['for'] & user.NEWUSER
            email = user_info['email']
            expire = time.time() + 60 * 60 * 24
            code = User.generate()

            change_name = self.get_argument('name', False)
            change_email = self.get_argument('email', False)
            change_pwd = self.get_argument('pwd', False)

            # for normal form submit
            if change_name == 'false':
                change_name = False
            if change_email == 'false':
                change_email = False
            if change_pwd == 'false':
                change_pwd = False

            assert change_name or change_email or change_pwd

            for_ = 0
            if change_name:
                for_ |= User.CHANGEUSER
            if change_email:
                for_ |= User.CHANGEEMAIL
            if change_pwd:
                for_ |= User.CHANGEPWD

        logger.info('user: %s; email: %s; for: %s, expire: %s, code: %s',
                    user_info['user'], email, action, expire, code)

        user.set_code(for_=for_, code=code, expire=expire)
        user.save()

        mail_man = Email(email, self.locale.code)

        try:
            mail_man.send('update_account',
                          user=user_info['user'],
                          code=code,
                          escaped_code=quote(code),
                          expire_announce=self.format_expire(expire))
        except BaseException as e:
            flag = self.ERROR_FAILED_SEND_EMAIL
            error = get_exc_plus()
            logger.error(error)
            Message().send(
                None,
                None,
                '''Fail to send to {user}({email}/{for_}).<br />
                <pre><code>{error}</code></pre>'''.format(
                    user=user_info['user'],
                    email=email,
                    for_=for_,
                    error=error
                    ))

        self.write(json.dumps({'error': flag, 'email': email}))
        self.finish()
        return

    def format_expire(self, t):
        if t is None:
            return ''
        if self.locale.code[:2].lower().startswith('zh'):
            return '请在%s前完成验证' % \
                    time.strftime('%Y年%m月%d日，%H:%M', time.localtime(t))

        return 'Please verify before' + time.ctime(t)
