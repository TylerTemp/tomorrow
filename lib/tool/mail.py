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

    def send(self, to, sub, content, subtype='html'):
        if 'zh_ch' in self.config.mail and self.is_zh_mail(to):
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

        logger.debug(sub)
        logger.debug(content)
        return True

        try:
            logger.debug('connecting %s', host)
            self.smtp.connect(host)
            logger.debug('logging...')
            self.smtp.login(me, pwd)
            logger.debug('sending...')
            self.smtp.sendmail(me, [to], msg.as_string())
            logger.debug('finished')
        except BaseException as e:
            logger.error('failed to send mail: %s', e)
            return False
        else:
            try:
                self.smtp.close()
            except BaseException as e:
                logger.error(e)

            return True

    def verify_new_mail(self, email, user, url):
        if self.lang.lower().startswith('en'):
            # english
            title = 'Welcome, {user} | tomorrow.becomes.today'
            content = '''\
<h2>Verify Your Email</h2>
<p>Hi, {user}. You've just registered at
    <a href="http://tomorrow.becomes.today">tomorrow.becomes.today</a>.
</p>
<p>Click the following link to active your account:<br/>
    <a href="http://tomorrow.becomes.today{url}">
        http://tomorrow.becomes.today{url}
    </a>
</p>
<p>If you can't click the url above, please copy the following text and paste
in you browser.</p>
<code>http://tomorrow.becomes.today{url}</code>'''
        else:
            title = '{user}，欢迎加入 | tomorrow.becomes.today'
            content = '''\
<h2>验证你的邮箱</h2>
<p>{user}，你好。你刚注册了
    <a href="http://tomorrow.becomes.today">tomorrow.becomes.today</a>。
</p>
<p>请点击以下链接来激活你的账户<br/>
    <a href="http://tomorrow.becomes.today{url}">
        http://tomorrow.becomes.today{url}
    </a>
</p>
<p>如果你无法点击上面的链接，请将下方文字粘贴到浏览器地址栏</p>
<code>http://tomorrow.becomes.today{url}</code>'''

        title = title.format(user=user)
        content = content.format(user=user, url=url)

        return self.send(email, title, content)

    @classmethod
    def is_zh_mail(cls, mail):
        return any(to.endswith(suffix) for suffix in cls.config.zh_mail_list)


if __name__ == '__main__':
    bashlog.stdoutlogger(logger=logger, level=bashlog.DEBUG, color=True)
    email = Email()
    email.send(to=email.config.mail['default']['user'],
               sub="Tomorrow Becomes Today",
               content="Here we go")
