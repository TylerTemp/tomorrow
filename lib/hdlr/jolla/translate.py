import tornado.web
import tornado.gen
import tornado.escape
import logging
import json
try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote
    from urlparse import unquote

from .base import BaseHandler
from lib.tool.md import html2md, md2html
from lib.tool.md import escape
from lib.db.jolla import Article, User, Source, Author

logger = logging.getLogger('tomorrow.jolla.translate')


class TranslateHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, slug=None):
        if slug is not None:
            article = Article(slug)
            link = article.source['link']
            return self.redirect('/tr/?source=%s' % quote(link, ''))
        link = self.get_argument('source')
        source = Source(link)
        if not source:
            raise tornado.web.HTTPError(404, 'link %r not found' % link)

        user = self.current_user
        article = Article.by_user_link(user._id, link)

        self.xsrf_token

        return self.render(
            'jolla/translate.html',
            link=(source.link or
                  (article.source and article.source['link']) or
                  None),
            source=source,
            article=article,
            imgs=None,
            files=None,
            size_limit=0,
        )

    @tornado.web.authenticated
    def post(self):
        self.check_xsrf_cookie()
        if self.get_argument('action', None) == 'preview':
            return self.preview()

        title = self.get_argument('title').strip()
        source_link = self.get_argument('source').strip()
        desc = self.get_argument('description', '').strip() or None
        content = self.get_argument('content').strip()

        banner = self.get_argument('banner', '').strip() or None
        cover = self.get_argument('cover', '').strip() or None
        ori_author = self.get_argument('original-author').strip()
        slug = self.get_argument('slug', '').strip() or None

        tag = []
        for each in self.get_argument('tag', '').split(','):
            t = each.strip()
            if t not in tag:
                tag.append(t)

        user = self.current_user

        source = Source(source_link)
        if not source:
            raise tornado.web.HTTPError(
                    500, 'Source %r not found' % source_link)

        if slug is None:
            slug = source.slug

        article = Article.by_user_link(user._id, source.link)
        article.title = title
        article.description = self.safe(desc)
        article.content = self.safe(content)
        article.banner = banner
        article.cover = cover
        article.tag = tag
        article.source = {'link': source.link, 'title': source.title,
                          'author': ori_author or source.author}
        article.slug = slug
        if not article.author:
            article.author = self.current_user._id
        if user.type < user.ROOT:
            self.save_for_normal(article, source)
        else:
            self.save_for_su(article, source)

        return self.write(json.dumps({
            'error': 0,
            'redirect': '//%s/%s/' % (self.config.jolla_host, article.slug)
        }))

    def preview(self):
        content = self.get_argument('content')
        original_author = self.get_argument('original-author').strip()
        desc = self.get_argument('description', '').strip() or None
        author = self.current_user

        if not desc:
            desc = tornado.escape.xhtml_escape(content[:100])
        else:
            desc = md2html(desc)
        content = md2html(content)
        original_author = Author(original_author)
        lang_code = self.locale.code[:2].lower()

        author_extra = getattr(author, lang_code)

        result = {
            'description': desc,
            'content': content,
            'author': {
                'name': author.name,
                'photo': author.photo,
                'donate':author_extra.get('donate', None),
                'intro':author_extra.get('intro', None),
            },
            'original_author': {
                'name': original_author.name,
                'photo': original_author.photo,
                'intro': original_author.intro,
            },
        }

        return self.write(json.dumps(result))

    def safe(self, content):
        if content is None:
            return None

        user = self.current_user
        if user.type >= user.ROOT:
            return content

        return escape(content)

    def save_for_normal(self, article, source):
        if not article:
            # New article
            if article.slug == source.slug:
                slug = '%s-by-%s' % (article.slug, self.current_user.name)
                index = 0
                while Article(slug):  # exists
                    index += 1
                    slug = '%s-by-%s-%s' % (article.slug,
                                            self.current_user.name,
                                            index)
                article.slug = slug

        article.save()

    def save_for_su(self, article, source):
        source.translated = article.slug
        article.status = article.ACCEPTED
        article.save()
        source.save()
        Article.eject_except(article._id)
