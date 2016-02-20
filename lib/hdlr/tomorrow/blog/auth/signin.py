from .base import BaseHandler
from lib.tool import url
from lib.db.tomorrow import User
from lib.tool.mail import Email
from lib.tool.tracemore import get_exc_plus
import logging

try:
    from urllib.parse import quote
except ImportError:
    from urlparse import quote

class SigninHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.auth.signin')
    USER_START_ERROR = 1
    USER_TOO_LONG = 2
    USER_INVALIDATE = 4
    USER_EXISTS = 8
    EMAIL_EXISTS = 16

    def get(self):
        user = email = None
        _user = self.get_argument('user', None)
        if _user is not None:
            if '@' in _user:
                email = _user
            else:
                user = _user
        return self.render(
            'tomorrow/blog/auth/signin.html',
            user=user,
            email=email,
            query=url.get_query(self.request.uri)
        )

    def post(self):
        name = self.get_argument('user')
        pwd = self.get_argument('pwd')
        email = self.get_argument('email')
        assert name
        assert pwd
        assert email and '@' in email

        error, messages = self.verify_name(name)
        error, msg = self.verify_email(email, error)
        if msg:
            messages.append(msg)

        if error != 0:
            message = '; '.join(messages)
            self.set_status(403, message)
            return self.write({
                'error': error,
                'message': message
            })

        user = User()
        user.name = name
        user.pwd = pwd
        user.email = email
        user.save()
        self.login(user, True)
        self.write({'error': 0,
                    'next': self.get_argument('next', None)})

        self.finish()
        self.send_signin_email(user)

    def verify_name(self, name, error=0):
        messages = []
        if name[0] in ' .':
            error |= self.USER_START_ERROR
            messages.append('User name should not start with %r' % name[0])

        if len(name) > self.USERMAX:
            error |= self.USER_TOO_LONG
            messages.append('User name should not be longer than %r' %
                            self.USERNAME)

        if not self.USERNAME.match(name):
            error |= self.USER_INVALIDATE
            messages.append(
                'User name should only contain Chinese characters, '
                'English letters, numbers and " ", ".", "-", "_"'
            )

        user = User(name)
        if user:
            error |= self.USER_EXISTS
            messages.append(
                'User name exists'
            )

        return error, messages

    def verify_email(self, email, error=0):
        message = None
        if User.find_one({'email': email}):
            error |= self.EMAIL_EXISTS
            message = 'Email has been registered'

        return error, message


    def send_signin_email(self, user):
        code = user.generate()
        address = user.email
        user.set_code(for_=user.NEWUSER, code=code)
        user.save()

        mail = Email()._with_logger(self.logger)
        content = mail.render(
            'new_user.html',
            self.locale.code[:2].lower(),
            name=user.name,
            code=code,
            quoted_code=quote(code, '')
        )

        title = ''.join((user.name, ', ', self.locale.translate('welcome to'),
                         ' tomorrow.comes.today'))
        try:
            mail.send(address, title, content)
        except BaseException:
            self.critical(get_exc_plus())
            raise
