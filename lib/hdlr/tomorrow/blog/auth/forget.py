import logging
import time
from .base import BaseHandler
from lib.db.tomorrow import User
from lib.tool.mail import Email
from lib.tool.tracemore import get_exc_plus
try:
    from urllib.parse import quote
except ImportError:
    from urlparse import quote


class ForgetHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.auth.forget')
    NOT_EXISTS = 1
    NO_EMAIL = 2
    FAIL_SEND_EMAIL = 3

    def get(self):
        return self.render(
            'tomorrow/blog/auth/forget.html',
            user=self.get_argument('user', None),
        )

    def post(self):
        self.check_xsrf_cookie()
        user = User(self.get_argument('user'))
        if not user:
            return self.set_code_with(
                404, {'error': self.NOT_EXISTS, 'message': 'User %r not exists' % user.name})

        address = user.email
        if not address:
            return self.set_code_with(
                403, {'error': self.NO_EMAIL,
                      'message': 'User %r has no email' % user.name}
            )

        expire_duration = 60 * 60 * 24
        if user.verify['code']:
            user.verify['for'] |= user.CHANGEPWD
            if user.verify['expire']:
                if user.verify['expire'] - time.time() < expire_duration:
                    user.verify['expire'] = time.time() + expire_duration
        else:
            code = user.generate()
            user.set_code(user.CHANGEPWD, code, time.time() + expire_duration)

        code = user.verify['code']
        assert code, code

        mail = Email()._with_logger(self.logger)
        content = mail.render('change_pwd.html', self.locale.code[:2].lower(),
                              name=str(user.name),
                              code=code,
                              quoted_code=quote(code, '')
                              )
        title = self.locale.translate(
            'Please confirm the changes on tomorrow.comes.today')

        try:
            mail.send(address, title, content)
        except BaseException:
            self.critical(get_exc_plus())
            return self.set_code_with(
                500, {'error': self.FAIL_SEND_EMAIL,
                      'message': 'Sending email to %r failed'})
        else:
            user.save()
            return self.write({'error': 0, 'address': address})

    def set_code_with(self, code, value):
        self.set_status(code)
        return self.write(value)
