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
from lib.hdlr.base import EnsureUser
from lib.db import Jolla, Article, User
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
            cover = article.get('cover', '')
        else:
            title = author = md = html = headimg = link = cover = ''

        use_md = self.get_argument('md', False)

        return self.render(
            'jolla/task.html',
            imgs=imgs,
            files=files,

            title=title,
            author=author,
            headimg=headimg,
            cover=cover,
            html=html,
            md=md,
            link=link,

            img_upload_url='/am/%s/img/' % quote(username),
            file_upload_url='/am/%s/file/' % quote(username),
            size_limit=cfg.size_limit[usertype],

            nav_active='jolla_task',
            use_md=use_md
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
        cover = self.get_argument('cover', None)

        if format == 'md':
            if self.current_user['type'] < User.root:
                content = escape(content)
        else:
            content = html2md(content)

        if url is None:
            article = Jolla()
            article.set(article.find_link(link))
        else:
            article = Jolla(unquote(url))

        new_task = article.new
        if new_task:
            article.add(link, title, author, content,
                        url=url, headimg=headimg, cover=cover, index=None)
        else:
            article.get().update({
                'link': link,
                'title': title,
                'author': author,
                'content': content,
                'url': url,
                'headimg': headimg,
                'cover': cover,
                'edittime': time.time(),
            })
        article.save()

        red_url = article.get()['url']
        redirect = '/jolla/translate/%s/' % quote(red_url)
        logger.debug("new jolla translate task: %s", title)
        self.write(json.dumps({'error': 0, 'redirect': redirect}))
        self.finish()

        # refresh cache
        coll = Article.get_collect()
        result = coll.update_many(
            {'board': 'jolla', 'transref': red_url},
            {'$set': {'transinfo.headimg': headimg, 'transinfo.cover': cover}})
        logger.debug('updated %s translation', result.modified_count)
