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
from .base import BaseHandler, EnsureUser

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db.tomorrow import Article, User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.blog.edit')


class EditHandler(BaseHandler):

    # @EnsureUser(level=User.root, active=True)
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
                  'description': '',
                  'author': user_name,
                  'email': user_info['email'],
                  'show_email': True}

        if urlslug is not None:
            article = Article(urlslug)
            if article.new:
                raise tornado.web.HTTPError(404, '%s not found' % urlslug)
            info = article.get()
            zh = info.pop('zh', None)
            en = info.pop('en', None)
            result['slug'] = info.pop('slug')
            result.update(info)
            result['title'] = ''
            result['content'] = ''
            result['description'] = ''
            if source == 'zh' and zh:
                result['title'] = zh['title']
                result['content'] = zh['content'] or ''
                result['description'] = zh['description'] or ''
            elif source == 'en' and en:
                result['title'] = en['title']
                result['content'] = en['content'] or ''
                result['description'] = en['description'] or ''

        return self.render(
            'tomorrow/blog/edit.html',
            nav_active='new_post',
            imgs=imgs,
            files=files,
            img_upload_url='/am/%s/img/' % user_slug,
            file_upload_url='/am/%s/file/' % user_slug,
            **result
        )

    # @EnsureUser(level=User.root, active=True)
    def post(self, urlslug=None):
        title = self.get_argument('title')
        slug = self.get_argument('slug')
        content = self.get_argument('content')

        tag = set()
        for each_tag in self.get_argument('tag', '').split(','):
            each = each_tag.strip()
            if each:
                tag.add(each)
        tag = list(tag)

        headimg = self.get_argument('headimg', None)
        cover = self.get_argument('cover', None)
        description = self.get_argument('description', None)
        board = self.get_argument('board', 'blog')
        lang = self.get_argument('language', 'zh')
        assert lang in ('zh', 'en')

        if description is not None:
            description = description.strip()

        new = True
        if urlslug:
            article = Article(unquote(urlslug))
            new = article.new
        if new:
            article = Article(slug)

        logger.info('%s new: %s', slug, article.new)
        result = {
            'slug': slug,
            'board': board or 'blog',
            lang: {
                'title': title,
                'content': content,
                'description': description or None,
            },
            'author': self.get_argument('author', None) or None,
            'email': self.get_argument('email', None) or None,
            'show_email': self.get_bool('show_email', False),
            'tag': tag,
            'headimg': headimg or None,
            'cover': cover or None,
            'index': None
        }

        if article.new:
            result.update({
                'createtime': time.time(),
                'edittime': time.time()
            })

        elif not self.get_argument('mirror', False):
            result['edittime'] = time.time()

        article.get().update(result)

        article.save()

        if board == 'jolla':
            re_slug = '/jolla/blog/%s/'
        else:
            re_slug = '/blog/%s/'

        return self.write(json.dumps({'error': 0,
                                      'redirect': re_slug % quote(slug)}))
