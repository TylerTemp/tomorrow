# coding: utf-8

import tornado.gen
import logging
import time
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
    # smtp = smtplib.SMTP()

    def __init__(self, lang='zh_CN'):
        self.lang = lang

    def _send_gmail(self, user, pwd, tos, msg):
        logger.info('send using %s', user)
        try:
            logger.info('connect to google')
            smtp = smtplib.SMTP('smtp.gmail.com:587')
            logger.info('say EHLO')
            smtp.ehlo()
            logger.info('starttls')
            smtp.starttls()
            logger.info('login...')
            smtp.login(user, pwd)
            logger.info('sending...')
            smtp.sendmail(user, tos, msg)
        except BaseException as e:
            logger.error('failed to send mail: %s', e)
            return False
        else:
            return True

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
            logger.error('failed to send mail: %s', e)
            return False
        else:
            return True

    def send(self, to, sub, content, subtype='html'):
        if 'zh_CN' in self.config.mail and self.is_zh_mail(to):
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

        if me.endswith('gmail.com'):
            return self._send_gmail(me, pwd, [to], msg.as_string())

        return self._send_normal(host, me, pwd, [to], msg.as_string())

    @tornado.gen.coroutine
    def verify_new_mail(self, email, user, code, url):
        if self.lang.lower().startswith('en'):
            # english
            title = 'Welcome, {user} | tomorrow.becomes.today'
            content = '''\
<h2>Verify Your Email</h2>
<p>Hi, {user}. You've just registered at
    <a href="http://tomorrow.becomes.today">tomorrow.becomes.today</a>.
</p>
<p>Your verifying code is <code>{code}</code></p>
<p>Click the following link to active your account:<br/>
    <a href="http://tomorrow.becomes.today{url}">
        http://tomorrow.becomes.today{url}
    </a>
</p>
<p>If you can't click the url above, please copy the following text and paste
in you browser.</p>
<p><code>http://tomorrow.becomes.today{url}</code></p>'''
        else:
            title = '{user}，欢迎加入 | tomorrow.becomes.today'
            content = '''\
<h2>验证你的邮箱</h2>
<p>嘿，{user}！你刚注册了
    <a href="http://tomorrow.becomes.today">tomorrow.becomes.today</a>。
</p>
<p>你的激活码是{code}</p>
<p>猛戳下方链接来激活你的账户:<br/>
    <a href="http://tomorrow.becomes.today{url}">
        http://tomorrow.becomes.today{url}
    </a>
</p>
<p>戳不了？把下面这行复制到浏览器地址栏也行 :)</p>
<p><code>http://tomorrow.becomes.today{url}</code></p>'''

        title = title.format(user=user)
        content = content.format(user=user, url=url, code=code)

        raise tornado.gen.Return(self.send(email, title, content))

    def _verify_change(self, email, user, code, url, expire, for_, ssl=False):
        if self.lang.lower().startswith('en'):

            title = 'Change your %s | tomorrow.becomes.today' % for_
            content = '''\
<h2>Change your {for}</h2>
<p>Hi, {user}! You request for changing your {for}.</p>
<p>Your verifying code is <code>{code}</code>. Use it before {time}</p>
<p>Click the following link to change {for}:<br/>
    <a href="http{s}://tomorrow.becomes.today{url}">
        http{s}://tomorrow.becomes.today{url}
    </a>
</p>
<p>If you can't click the url above, please copy the following text and paste
in you browser.</p>
<p><code>http{s}://tomorrow.becomes.today{url}</code></p>'''
        else:
            title = '修改你的%s | tomorrow.becomes.today' % for_
            content = '''\
<h2>修改你的{for}</h2>
<p>嘿，{user}！ 你申请修改{for}.</p>
<p>你的验证码是：<code>{code}</code>。该验证码在{time}前有效</p>
<p>猛戳下方连接完成修改：<br/>
    <a href="http{s}://tomorrow.becomes.today{url}">
        http{s}://tomorrow.becomes.today{url}
    </a>
</p>
<p>点不动？把下面这行复制到浏览器地址栏吧</p>
<p><code>http{s}://tomorrow.becomes.today{url}</code></p>'''

        content = content.format(**{'for': for_, 'user': user, 'code': code,
                                    'url': url, 'time': expire,
                                    's':'s' if ssl else ''})
        return self.send(email, title, content)

    @tornado.gen.coroutine
    def verify_change_mail(self, email, user, code, url, expire):
        if self.is_en():
            for_ = 'email'
        else:
            for_ = '邮箱'

        raise tornado.gen.Return(self._verify_change(email, user, code, url,
                                                     self.format_time(expire),
                                                     for_))

    @tornado.gen.coroutine
    def verify_change_user(self, email, user, code, url, expire):
        if self.is_en():
            for_ = 'user name'
        else:
            for_ = '用户名'

        raise tornado.gen.Return(self._verify_change(email, user, code, url,
                                                     self.format_time(expire),
                                                     for_))

    @tornado.gen.coroutine
    def verify_change_pwd(self, email, user, code, url, expire):
        if self.is_en():
            for_ = 'password'
        else:
            for_ = '密码'

        raise tornado.gen.Return(self._verify_change(email, user, code, url,
                                                     self.format_time(expire),
                                                     for_, ssl=True))

    @classmethod
    def is_zh_mail(cls, mail):
        return any(mail.endswith(suffix) for suffix in cls.config.zh_mail_list)

    def is_en(self):
        return self.lang.lower().startswith('en')

    def format_time(self, t):
        if self.is_en():
            return time.ctime(t)
        return time.strftime('%Y年%m月%d日，%H:%M', time.localtime(t))

if __name__ == '__main__':
    bashlog.stdoutlogger(logger=logger, level=bashlog.DEBUG, color=True)
    email = Email('zh')
    email.send(to=email.config.mail['default']['user'],
               sub="Tomorrow Becomes Today",
               content="Here we go")
