import tornado.web
import logging
import json
import time
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler, EnsureUser
from lib.db import Article, User
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.edit')


class EditHandler(BaseHandler):

    @EnsureUser(level=User.root, active=True)
    def get(self, urlslug=None):

        if self.get_argument('test', False):
            test_slug = self.get_argument('slug').strip()
            if test_slug == 'en':
                result = '0'
            elif test_slug == urlslug:
                result = '-1'
            else:
                result = str(int(Article(test_slug).new))
            return self.write(result)

        user_info = self.current_user
        user_name = user_info['user']
        user_slug = quote(user_name)
        imgs, files = self.get_imgs_and_files(user_name, user_info['type'])
        source = self.get_argument('source', 'zh')

        result = {'title': '',
                  'slug': urlslug,
                  'lang': source,
                  'content': '',
                  'board': 'blog',
                  'tag': [],
                  'headimg': '',
                  'cover': '',
                  'description': ''}

        if urlslug is not None:
            article = Article(urlslug)
            if article.new:
                raise tornado.web.HTTPError(404, '%s not found' % urlslug)
            info = article.get()
            zh = info.pop('zh', None)
            en = info.pop('en', None)
            result['slug'] = info.pop('slug')
            result.update(info)
            if source == 'zh':
                result['title'] = zh['title']
                result['content'] = zh['content'] or ''
                result['description'] = zh['description'] or ''
            else:
                result['title'] = en['title']
                result['content'] = en['content'] or ''
                result['description'] = en['description'] or ''

        return self.render(
            'edit.html',
            nav_active='new_post',
            imgs=imgs,
            files=files,
            img_upload_url='/am/%s/img/' % user_slug,
            file_upload_url='/am/%s/file/' % user_slug,
            **result
        )

    @EnsureUser(level=User.root, active=True)
    def post(self, urlslug=None):
        title = self.get_argument('title')
        slug = self.get_argument('slug')
        content = self.get_argument('content')

        tag = [x.strip() for x in self.get_argument('tag', '').split(',')]
        headimg = self.get_argument('headimg', None)
        cover = self.get_argument('cover', None)
        description = self.get_argument('description', None)
        board = self.get_argument('board', 'blog')
        lang = self.get_argument('language', 'zh')
        assert lang in ('zh', 'en')

        if description is not None:
            description = description.strip()

        article = Article(slug)
        logger.info('%s new: %s', slug, article.new)
        result = {
            'board': board or 'blog',
            lang: {
                'title': title,
                'content': content,
                'description': description or None,
            },
            'author': self.current_user['user'],
            'email': self.current_user['email'],
            'show_email': True,
            'tag': tag,
            'headimg': headimg or None,
            'cover': cover or None,
            'index': None}

        if article.new:
            result.update({
                'createtime': time.time(),
                'edittime': time.time()
            })

        article.get().update(result)

        article.save()

        return self.write(json.dumps({'error': 0,
                                      'redirect': '/blog/%s/' % quote(slug)}))
