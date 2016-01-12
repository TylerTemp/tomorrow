import tornado.web
import logging
import json
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote
from .base import BaseHandler
from ..base import EnsureUser

from lib.db.tomorrow import Article, User

logger = logging.getLogger('tomorrow.blog.edit')


class EditHandler(BaseHandler):

    @EnsureUser(level=User.ROOT, active=True)
    def get(self, urlslug=None):
        if self.get_argument('test', False):
            return self.check_slug(self.get_argument('slug'), urlslug)

        user = self.current_user
        user_name = user.name
        user_slug = quote(user_name)
        if user.type >= user.ADMIN:
            imgs, files = self.get_imgs_and_files(user_name)
        else:
            imgs, files = None, None

        source = self.get_argument('source', 'zh')

        if urlslug is not None:
            article = Article(urlslug, source)
            if not article:
                raise tornado.web.HTTPError(404, '%s not found' % urlslug)
        else:
            article = Article(urlslug, source)

        return self.render(
            'tomorrow/blog/edit.html',
            nav_active='new_post',
            imgs=imgs,
            files=files,
            img_upload_url='/am/%s/img/' % user_slug,
            file_upload_url='/am/%s/file/' % user_slug,
            article=article,
            user=user
        )

    def check_slug(self, slug, this_slug):
        if slug == this_slug:
            result = -1
        else:
            result = int(not bool(Article(slug)))
        return self.write(str(result))

    @EnsureUser(level=User.ROOT, active=True)
    def post(self, urlslug=None):
        title = self.get_argument('title')
        slug = self.get_argument('slug')
        content = self.get_argument('content')

        tag = []
        for each_tag in self.get_argument('tag', '').split(','):
            each = each_tag.strip()
            if each and each not in tag:
                tag.append(each)

        description = self.get_argument('description', None)
        lang = self.get_argument('language', 'zh')
        assert lang in ('zh', 'en')

        if description is not None:
            description = description.strip() or None

        if urlslug:
            article = Article(unquote(urlslug), lang=lang)
            if not article:
                raise tornado.web.HTTPError(404, '%s not found' % urlslug)
        else:
            article = Article(lang=lang)

        article.slug = slug
        article.title = title
        article.content = content
        article.description = description
        article.author = self.current_user.name
        article.show_email = self.get_argument('show_email', False) or False
        article.tag = tag
        article.banner = self.get_argument('banner', None)
        article.cover = self.get_argument('cover', None)

        article.save()

        return self.write(json.dumps(
            {'error': 0, 'redirect': '/blog/%s/' % quote(slug)}))
