import tornado.web
import logging
import json
import time
try:
    from urllib.parse import quote
    from urllib.parse import unquote
    from urllib.parse import urljoin
    from urllib.parse import urlsplit
except ImportError:
    from urllib import quote
    from urlparse import unquote, urljoin, urlsplit

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
    def get(self, urlslug=None):
        self.xsrf_token
        user_info = self.get_current_user()
        username = user_info['user']
        usertype = user_info['type']

        imgs, files = self.get_imgs_and_files(
            username, usertype)

        if urlslug is not None:
            article = Jolla.find_slug(unquote(urlslug))
            if article is None:
                raise tornado.web.HTTPError(
                    404, "article %s not found" % urlslug)
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
            slug = article['slug'] or ''
            tag = article['tag']
            # description = article.get('description', '')
        elif urlslug is not None:
            raise tornado.web.HTTPError(404, "task %s not found" % urlslug)
        else:
            title = author = md = html = headimg = link = cover = slug = ''
            tag = []
            # description = slug = ''

        use_md = self.get_argument('md', False)
        content = md if use_md else html

        return self.render(
            'jolla/task.html',
            imgs=imgs,
            files=files,

            title=title,
            author=author,
            headimg=headimg,
            cover=cover,
            # html=html,
            # md=md,
            # description=description,
            content=content,
            link=link,
            slug=slug,
            tag=tag,

            img_upload_url='/am/%s/img/' % quote(username),
            file_upload_url='/am/%s/file/' % quote(username),
            size_limit=cfg.size_limit[usertype],

            nav_active='jolla_task',
            use_md=use_md
        )

    @EnsureUser(level=User.admin, active=True)
    def post(self, urlslug=None):
        logger.debug('post...')
        self.check_xsrf_cookie()
        link = self.get_argument('link')
        title = self.get_argument('title')
        author = self.get_argument('author')
        content = self.get_argument('content')
        format = self.get_argument('format')
        headimg = self.get_argument('headimg', None) or None
        cover = self.get_argument('cover', None) or None
        slug = self.get_argument('slug', None) or None
        tag = [x.strip() for x in self.get_argument('tag', '').split(',')]

        sp = urlsplit(link)
        if not sp.netloc:
            link = 'http://' + link

        if format == 'md':
            if self.current_user['type'] < User.root:
                logger.debug('escape for md')
                content = escape(content)
        # 'html'
        elif self.current_user['type'] < User.root:
            logger.debug('html -> md')
            content = html2md(content)

        if urlslug is None:
            article = Jolla()
            article.set(article.find_link(link))
        else:
            article = Jolla(unquote(urlslug))

        new_task = article.new
        if new_task:
            article.add(link, title, author, content,
                        slug=slug, headimg=headimg, cover=cover, index=None,
                        tag=tag)
        else:
            article.get().update({
                'link': link,
                'title': title,
                'author': author,
                'content': content,
                'slug': slug,
                'headimg': headimg,
                'cover': cover,
                'edittime': time.time(),
                'tag': tag
            })
        article.save()

        red_url = article.get()['slug']
        redirect = '/jolla/tr/%s/' % quote(red_url)
        logger.debug("new jolla translate task: %s", title)
        self.write(json.dumps({'error': 0, 'redirect': redirect}))
        self.finish()

        # refresh cache
        coll = Article.get_collect()
        result = coll.update_many(
            {'board': 'jolla', 'transinfo.slug': red_url},
            {'$set': {'headimg': headimg, 'cover': cover, 'tag': tag}})
        logger.debug('updated %s translation', result.modified_count)
