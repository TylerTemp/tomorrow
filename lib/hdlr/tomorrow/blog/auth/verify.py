import logging
import time
from .signin import SigninHandler
from lib.db.tomorrow import User

class VerifyHandler(SigninHandler):
    logger = logging.getLogger('tomorrow.auth.verify')

    def get(self):
        code=self.get_argument('code', None)
        if not code:
            return self.render('tomorrow/blog/auth/input-verify.html')

        self.debug(code)
        user = User.find_one({'verify.code': code})
        if not user:
            error = 'notfound'
        elif 'expire' in user.verify and time.time() > user.verify['expire']:
            del user.verify
            user.save()
            error = 'expire'
        else:
            return self.render(
                'tomorrow/blog/auth/verify.html',
                user=user,
                code=code,
            )

        self.set_status(403, error)
        return self.render(
            'tomorrow/blog/auth/error-verify.html',
            error=error
        )

    def post(self):
        code = self.get_argument('code', None)
        user = User.find_one({'verify.code': code})
        for_ = user.verify['for']
        if 'expire' in user.verify and time.time() > user.verify['expire']:
            self.set_status(403, 'expired')
            user.__info__.pop('verify')
            user.save()
            return self.write({
                'error': -2,
                'message': 'code expired'
            })

        if for_ & user.NEWUSER:
            user.active = True

        error = 0
        messages = []
        if not user.name or for_ & user.CHANGEUSER:
            name = self.get_argument('name')
            if name != user.name:
                error, messages = self.verify_name(name)

        if not user.email or for_ & user.CHANGEEMAIL:
            email = self.get_argument('email')
            if email != user.email:
                error, msg = self.verify_email(email)
                if msg:
                    messages.append(msg)

        if not user.pwd or for_ & user.CHANGEPWD:
            pwd = self.get_argument('pwd')
            user.pwd = pwd

        if error == 0:
            user.__info__.pop('verify')
            user.save()
            self.login(user)
            return self.write({
                'error': 0
            })

        return self.write({
            'error': error,
            'message': '; '.join(messages)
        })
