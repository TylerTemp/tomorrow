# coding: utf-8

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from lib import Log
from lib.config.base import Config


class Email(Log):
    config = Config()
    logger = logging.getLogger('email')

    def _send_gmail(self, user, pwd, tos, msg):
        self.info('send using %s', user)
        self.debug('connect to google')
        smtp = smtplib.SMTP('smtp.gmail.com:587')
        try:
            self.debug('say EHLO')
            smtp.ehlo()
            self.debug('starttls')
            smtp.starttls()
            self.debug('login...')
            smtp.login(user, pwd)
            self.debug('sending...')
            smtp.sendmail(user, tos, msg)
        finally:
            smtp.quit()

    def _send_normal(self, host, user, pwd, tos, msg):
        self.info('send using %s', user)
        smtp = smtplib.SMTP()
        try:
            self.debug('connecting %s', host)
            smtp.connect(host)
            self.debug('logging...')
            smtp.login(user, pwd)
            self.debug('sending...')
            smtp.sendmail(user, tos, msg)
            self.debug('finished')
        finally:
            smtp.quit()

    def send(self, to, title, content, by=None):
        if by is None:
            if 'zh_CN' in self.config.mail and self.is_zh_mail(to):
                self.debug('send by zh mail')
                by = self.config.mail['zh_CN']
            else:
                self.debug('send by default mail')
                by = self.config.mail['default']

        me = by['user']
        pwd = by['password']
        host = by['host']

        msg = MIMEMultipart()
        msg['Subject'] = title
        msg['From'] = me
        msg['To'] = to

        textpart = MIMEText(content, _subtype='html')
        msg.attach(textpart)

        if me.endswith('gmail.com'):
            return self._send_gmail(me, pwd, [to], msg.as_string())

        return self._send_normal(host, me, pwd, [to], msg.as_string())

    def is_zh_mail(self, mail):
        return any(mail.endswith(suffix) for suffix in self.config.zh_mail_list)

    @classmethod
    def render(cls, template, language, **kwargs):
        root = cls.config.root
        path = os.path.join(root, 'lib', 'mail', template)
        if language == 'zh':
            prefix, suffix = os.path.splitext(template)
            lang_path = ''.join((prefix, '.zh', suffix))
            if os.path.exists(lang_path):
                path = lang_path

        cls.logger.debug('render %s with %r',
                         path, kwargs)

        with open(path, 'r', encoding='utf-8') as f:
            return f.read().format(**kwargs)
