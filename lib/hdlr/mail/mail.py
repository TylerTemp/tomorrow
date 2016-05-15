from lib.hdlr.base import BaseHandler


class MailHandler(BaseHandler):

    def get(self):
        return self.render('mail/mail.html')
