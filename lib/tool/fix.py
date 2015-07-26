# coding: utf-8
# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote, quote

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import Email
sys.path.pop(0)

Email._email.drop()

info = (
    {'name': '_extra',
     'zh': {
        'main_title': 'tomorrow.becomes.today',
        'footer': ''
     },
     'default': {
        'main_title': 'tomorrow.becomes.today',
        'footer': ''
     }
    },
    {'name': 'new_user',
     'default':
        {'title': 'Welcome, {user}',
         'content': '''<h2>Verify Your Email</h2>
         <p>Hi, {user}. You've just registered at
           <a href="http://tomorrow.becomes.today">tomorrow.becomes.today</a>.
         </p>
         <p>Your verifying code is: <code>{code}</code></p>
         <p>Click the following link to active your account:<br/>
           <a href="http://tomorrow.becomes.today/verify/{escaped_code}/">
             https://tomorrow.becomes.today/verify/{escaped_code}/
           </a>
         </p>
         <p>If you can't click the url above, please copy the following text and paste
         in you browser.</p>
         <p><code>https://tomorrow.becomes.today/verify/{escaped_code}/</code></p>'''},
     'zh':
        {'title': '{user}，欢迎加入',
         'content': '''<h2>验证你的邮箱</h2>
         <p>嘿，{user}！你刚注册了
           <a href="http://tomorrow.becomes.today">tomorrow.becomes.today</a>。
         </p>
         <p>你的激活码是：{code}</p>
         <p>猛戳下方链接来激活你的账户:<br/>
          <a href="https://tomorrow.becomes.today/verify/{escaped_code}/">
            https://tomorrow.becomes.today/verify/{escaped_code}/
          </a>
         </p>
         <p>戳不了？把下面这行复制到浏览器地址栏也行 :)</p>
         <p><code>https://tomorrow.becomes.today/verify/{escaped_code}/</code></p>''',
        }
    },
    {'name': 'change_email',
     'default':
        {'title': 'Verify Your New Email Address',
         'content': '''<h1>Verify Your New Email Address</h1>
         <p>Hi {user}, you just changed your email address on
            <a href="http://tomorrow.becomes.today">tomorrow.becomes.today</a>.
         </p>
         <p>Your verifying code is: <code>{code}</code></p>
         <p>Click the following link to active your account:<br/>
           <a href="http://tomorrow.becomes.today/verify/{escaped_code}/">
             https://tomorrow.becomes.today/verify/{escaped_code}/
           </a>
         </p>
         <p>If you can't click the url above, please copy the following text and paste
         in you browser.</p>
         <p><code>https://tomorrow.becomes.today/verify/{escaped_code}/</code></p>'''},
     'zh':
        {'title': '验证你的新邮箱地址',
         'content': '''<h1>验证你的新邮箱地址</h1>
          <p>嘿，{user}。你刚修改了在我们站点
             <a href="http://tomorrow.becomes.today">tomorrow.becomes.today</a>
            的邮箱地址。
          </p>
          <p>你的激活码是：{code}</p>
          <p>猛戳下方链接来激活你的账户:<br/>
           <a href="https://tomorrow.becomes.today/verify/{escaped_code}/">
             https://tomorrow.becomes.today/verify/{escaped_code}/
           </a>
          </p>
          <p>戳不了？把下面这行复制到浏览器地址栏也行 :)</p>
          <p><code>https://tomorrow.becomes.today/verify/{escaped_code}/</code></p>'''}},
    {'name': 'update_account',
     'default':
        {'title': 'New Activity of Your Account',
         'content': '''<h1>Update Your Account</h1>
         <p>Hi, {user}. There are some changes of your account on
            <a href="http://tomorrow.becomes.today">tomorrow.becomes.today</a>.
         </p>
         <p>Your verifying code is: <code>{code}</code></p>
         <p>{expire_announce}</p>
         <p>Click the following link to active your account:<br/>
           <a href="http://tomorrow.becomes.today/verify/{escaped_code}/">
             https://tomorrow.becomes.today/verify/{escaped_code}/
           </a>
         </p>
         <p>If you can't click the url above, please copy the following text and paste
         in you browser.</p>
         <p><code>https://tomorrow.becomes.today/verify/{escaped_code}/</code></p>'''},
     'zh':
        {'title': '账户变更',
         'content':'''<h1>账户变更确认</h1>
          <p>嘿，{user}。你刚修改了在我们站点
             <a href="http://tomorrow.becomes.today">tomorrow.becomes.today</a>
            的账户信息。
          </p>
          <p>你的激活码是：{code}</p>
          <p>{expire_announce}</p>
          <p>猛戳下方链接来激活你的账户:<br/>
           <a href="https://tomorrow.becomes.today/verify/{escaped_code}/">
             https://tomorrow.becomes.today/verify/{escaped_code}/
           </a>
          </p>
          <p>戳不了？把下面这行复制到浏览器地址栏也行 :)</p>
          <p><code>https://tomorrow.becomes.today/verify/{escaped_code}/</code></p>'''}},
    {'name': 'invite',
     'default':
        {'title': 'Join Us',
         'content': '''<h1>Join Us and Create Something Awesome Together!</h1>
         <p>Hi there!</p>
         <p>{invitor} invite you to join
           <a href="https://tomorrow.becomes.today">
             tomorrow.becomes.today
           </a>.
         </p>
         <p>Your verifying code is: <code>{code}</code></p>
         <p>Click the following link to active your account:<br/>
           <a href="http://tomorrow.becomes.today/verify/{escaped_code}/">
             https://tomorrow.becomes.today/verify/{escaped_code}/
           </a>
         </p>
         <p>If you can't click the url above, please copy the following text and paste
         in you browser.</p>
         <p><code>https://tomorrow.becomes.today/verify/{escaped_code}/</code></p>'''},
     'zh':
        {'title': '加入我们',
         'content': '''<h1>现在就加入我们！</h1>
         <p>嘿，你好：</p>
         <p>{invitor}邀请你加入
           <a href="https://tomorrow.becomes.today/">
             tomorrow.becomes.today
           </a>。
         </p>
         <p>你的激活码是：{code}</p>
         <p>{expire_announce}</p>
         <p>猛戳下方链接来激活你的账户:<br/>
          <a href="https://tomorrow.becomes.today/verify/{escaped_code}/">
            https://tomorrow.becomes.today/verify/{escaped_code}/
          </a>
         </p>
         <p>戳不了？把下面这行复制到浏览器地址栏也行 :)</p>
         <p><code>https://tomorrow.becomes.today/verify/{escaped_code}/</code></p>'''}},
    {'name': 'invite_no_verify',
     'defualt':
        {'title': 'Welcome',
         'content': '''<h1>Welcome, My Friend</h1>
         <p>{invitor} just added you as a member of
             <a href="https://tomorrow.becomes.today/">
               tomorrow.becomes.today
             </a>.
         </p>
         <p>He/She should already give you the password. You can login on
            <a href="https://tomorrow.becomes.today/login/">
                tomorrow.becomes.today/login/
            </a>.
         </p>
         <p>Hope you enjoy there:)</p>'''},
    'zh':
        {'title': '欢迎',
         'content': '''<h1>欢迎加入</h1>
         <p>{invitor}刚添加了你为
             <a href="https://tomorrow.becomes.today/">
               tomorrow.becomes.today
             </a>成员。
         </p>
         <p>你应该已经从他/她那里获得了密码。你可以通过
            <a href="https://tomorrow.becomes.today/login/">
                tomorrow.becomes.today/login/
            </a>登录。
         </p>
         <p>希望你玩的开心:)</p>'''}}
)


for each in info:
    e = Email()
    print(each['name'])
    e.get().update(each)
    e.save()
