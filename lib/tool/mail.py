# coding: utf-8

import tornado.gen
import logging
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.config import Config
from lib.tool import bashlog
from lib.db import File, Email as Maildb
sys.path.pop(0)

logger = logging.getLogger('tomorrow.email')


class Email(object):
    config = Config()

    def __init__(self, to, lang='zh'):
        self.is_zh = lang[:2].lower().startswith('zh')
        self.to = to

    @classmethod
    def _send_gmail(self, user, pwd, tos, msg):
        logger.info('send using %s', user)
        logger.debug('connect to google')
        smtp = smtplib.SMTP('smtp.gmail.com:587')
        try:
            logger.debug('say EHLO')
            smtp.ehlo()
            logger.debug('starttls')
            smtp.starttls()
            logger.debug('login...')
            smtp.login(user, pwd)
            logger.debug('sending...')
            smtp.sendmail(user, tos, msg)
        except BaseException as e:
            logger.error(e)
            raise
        finally:
            smtp.quit()

    @classmethod
    def _send_normal(self, host, user, pwd, tos, msg):
        logger.info('send using %s', user)
        smtp = smtplib.SMTP()
        try:
            logger.debug('connecting %s', host)
            smtp.connect(host)
            logger.debug('logging...')
            smtp.login(user, pwd)
            logger.debug('sending...')
            smtp.sendmail(user, tos, msg)
            logger.debug('finished')
        except BaseException as e:
            logger.error(e)
            raise
        finally:
            smtp.quit()

    def send(self, name, **kwargs):
        mail_data = Maildb(name)
        assert not mail_data.new

        if 'zh_CN' in self.config.mail and self.is_zh_mail(self.to):
            logger.debug('send by zh mail')
            mailinfo = self.config.mail['zh_CN']
        else:
            logger.debug('send by default mail')
            mailinfo = self.config.mail['default']

        mail_content = mail_data.format(self.is_zh)

        me = mailinfo['user']
        pwd = mailinfo['password']
        host = mailinfo['host']

        msg = MIMEMultipart()
        msg['Subject'] = mail_content['title'].format(kwargs)
        msg['From'] = me
        msg['To'] = self.to

        textpart = MIMEText(
            mail_content['content'].format(**kwargs),
            _subtype='html')
        msg.attach(textpart)
        for file_info in mail_content.get('attachment', ()):
            name = file_info['name']
            content = file_info['content']
            filepart = MIMEApplication(content)
            filepart.add_header(
                'Content-Disposition',
                'attachment',
                filename=name)
            msg.attach(filepart)

        if me.endswith('gmail.com'):
            return self._send_gmail(me, pwd, [self.to], msg.as_string())

        return self._send_normal(host, me, pwd, [self.to], msg.as_string())

    @classmethod
    def is_zh_mail(cls, mail):
        return any(mail.endswith(suffix) for suffix in cls.config.zh_mail_list)


if __name__ == '__main__':
    bashlog.stdoutlogger(logger=logger, level=bashlog.DEBUG, color=True)
    email = Email('zh')
    email.send(to=email.config.mail['default']['user'],
               sub="Tomorrow Becomes Today",
               content="Here we go")
