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
from .base import BaseHandler


class SecureHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.dash.secure')

    ERROR_FAILED_SEND_EMAIL = 1
    ERROR_NOTHING_TO_SEND = 2

    @tornado.web.authenticated
    def get(self):

        user = self.current_user

        verify_mail = (user.verify and
                       user.verify['for'] & user.NEWUSER)

        return self.render(
            'tomorrow/admin/dash/secure.html',
            verify_mail=verify_mail,
            user=user
        )

    @tornado.web.authenticated
    def post(self):

        user = self.current_user

        action = self.get_argument('action', None)  # resend/verify_email/None
        verify = user.verify
        if action == 'resend':
            if not verify or verify['for'] == 0:
                self.write(json.dumps({'error': self.ERROR_NOTHING_TO_SEND}))
                self.finish()
                return
            expire = verify.get('expire', None)
            email = user.email
            code = verify['code']
            for_ = verify['for']
        elif action == 'verify_email':
            assert verify['for'] & user.NEWUSER
            email = self.get_argument('email')
            expire = None
            code = verify['code']
            for_ = verify['for']
        else:
            if verify and verify.get('code', None):
                assert verify['for'] & user.NEWUSER
            email = user.email
            expire = time.time() + 60 * 60 * 24
            code = User.generate()

            change_name = self.get_argument('name', False)
            change_email = self.get_argument('email', False)
            change_pwd = self.get_argument('pwd', False)

            assert change_name or change_email or change_pwd

            for_ = 0
            if change_name:
                for_ |= User.CHANGEUSER
            if change_email:
                for_ |= User.CHANGEEMAIL
            if change_pwd:
                for_ |= User.CHANGEPWD

        self.info('user: %s; email: %s; for: %s, expire: %s, code: %s',
                  user, email, action, expire, code)

        user.set_code(for_=for_, code=code, expire=expire)
        user.save()
        result = self.send_mail(user)
        if result:
            error = 0
        else:
            error = 1
        return self.write({'error': error})

    def send_mail(self, user):
        verify = user.verify
        code = verify['code']
        mail = Email()._with_logger(self.logger)

        title = '{name}, {title}'.format(
            name=user.name,
            title=self.locale.translate(
                'Please confirm the changes on tomorrow.comes.today'),
        )

        content = mail.render(
            'code.html',
            self.locale.code[:2].lower(),
            name=user.name,
            code=code,
            quoted_code=quote(code, '')
        )

        try:
            mail.send(user.email, title, content)
        except BaseException:
            self.critical(get_exc_plus())
            return False
        else:
            return True
