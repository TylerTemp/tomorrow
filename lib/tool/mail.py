# coding: utf-8

import logging
import atexit
import smtplib
from email.mime.text import MIMEText

import os
import sys

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.config import Config
from lib.tool import bashlog
sys.path.pop(0)

logger = logging.getLogger('tomorrow.email')

class Email(object):
    config = Config()
    smtp = smtplib.SMTP()

    def __init__(self, lang='zh_CN'):
        self.lang = lang

    def send(self, to, sub, content, subtype='plain'):
        if  'zh_ch' in self.config.mail and self.is_zh_mail(to):
            logger.debug('send by zh mail')
            mailinfo = self.config.mail['zh_CN']
        else:
            logger.debug('send by default mail')
            mailinfo = self.config.mail['default']

        me = mailinfo['user']
        pwd = mailinfo['password']
        host = mailinfo['host']

        msg = MIMEText(content, _subtype=subtype, _charset='utf-8')
        msg['Subject'] = sub
        msg['From'] = me
        msg['To'] = to

        try:
            logger.debug('connecting %s', host)
            self.smtp.connect(host)
            logger.debug('logging...')
            self.smtp.login(me, pwd)
            logger.debug('sending...')
            self.smtp.sendmail(me, [to], msg.as_string())
            logger.debug('finished')
            return True
        except Exception as e:
            logger.error('failed to send mail: %s', e)
            return False

    @classmethod
    def is_zh_mail(cls, mail):
        return any(to.endswith(suffix) for suffix in cls.config.zh_mail_list)


@atexit.register
def close():
    Email.smtp.close()


if __name__ == '__main__':
    bashlog.stdoutlogger(logger=logger, level=bashlog.DEBUG, color=True)
    email = Email()
    email.send(to=email.config.mail['default']['user'],
               sub="Tomorrow Becomes Today",
               content="Here we go")
