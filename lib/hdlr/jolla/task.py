import tornado.web
import logging
import json
import time
try:
    from urllib.parse import quote
    from urllib.parse import unquote
    from urllib.parse import urljoin
except ImportError:
    from urlparse import quote
    from urlparse import unquote
    from urlparse import urljoin

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.config import Config
from lib.tool.md import md2html
from lib.tool.md import html2md
from lib.tool.md import escape
from lib.tool.ensure import EnsureUser
from lib.db import Jolla
from lib.db import User
sys.path.pop(0)

cfg = Config()
logger = logging.getLogger('tomorrow.jolla.task')


class TaskHandler(BaseHandler):

    @EnsureUser(level=User.admin, active=True)
    def get(self, url=None):
        self.xsrf_token
        user_info = self.get_current_user()
        username = user_info['user']
        usertype = user_info['type']

        imgs, files = self.get_imgs_and_files(
            username, usertype)

        if url is not None:
            article = Jolla.find_url(unquote(url))
        else:
            article = None

        if article is not None:
            title = article['title']
            author = article['author']
            md = article['content']
            html = md2html(md)
            headimg = article['headimg']
            link = article['link']
        else:
            title = author = md = html = headimg = link = ''

        return self.render(
            'jolla/task.html',
            imgs=imgs,
            files=files,

            title=title,
            author=author,
            headimg=headimg,
            html=html,
            md=md,
            link=link,

            img_upload_url='/hi/%s/img/' % quote(username),
            file_upload_url='/hi/%s/file/' % quote(username),
            size_limit=cfg.size_limit[usertype]
        )

    @EnsureUser(level=User.admin, active=True)
    def post(self, url=None):
        logger.debug('post...')
        self.check_xsrf_cookie()
        link = self.get_argument('link')
        title = self.get_argument('title')
        author = self.get_argument('author')
        content = self.get_argument('content')
        format = self.get_argument('format')
        headimg = self.get_argument('headimg', None)

        if format == 'md':
            content = escape(content)
        else:
            content = html2md(content)

        if url is not None:
            url = unquote(url)

        article = Jolla(url)
        if article.new:
            article.add(link, title, author, content, url=url, headimg=headimg)
        else:
            article.get().update({
                'link': link,
                'title': title,
                'author': author,
                'content': content,
                'url': url,
                'headimg': headimg,
                'edittime': time.time(),
            })
        article.save()

        red_url = article.get()['url']
        redirect = '/jolla/translate/%s/' % quote(red_url)
        logger.debug("new jolla translate task: %s", title)
        return self.write(json.dumps({'error': 0, 'redirect': redirect}))
