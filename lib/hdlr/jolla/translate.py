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



class TranslateHandler(BaseHandler):
    logger = logging.getLogger('jolla.translate')

    @tornado.web.authenticated
    def get(self, slug=None):
        if slug is not None:
            article = Article(slug)
            link = article.source['link']
            return self.redirect('/tr/?source=%s' % quote(link, ''))
        if self.get_argument('action', None) == 'preview':
            return self.preview()
        link = self.get_argument('source')
        source = Source(link)
        if not source:
            raise tornado.web.HTTPError(404, 'link %r not found' % link)

        user = self.current_user
        article = Article.by_user_link(user._id, link)

        self.xsrf_token

        return self.render(
            'jolla/translate.html',
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

        article = Article.by_user_link(user._id, source.link)
        article.slug = self.get_slug(slug, article, source)

        article.title = title
        article.description = self.safe(desc)
        article.content = self.safe(content)
        article.banner = banner
        article.cover = cover
        article.tag = tag
        article.source = {'link': source.link, 'title': source.title,
                          'author': ori_author or source.author}

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

    def get_slug(self, slug, article, source):
        if slug is None:  # auto-set slug
            if article.slug is not None:
                return article.slug

            return self._make_slug(article, source)

        if article.slug == slug:
            return slug

        exists = Article(slug)
        if exists and exists._id != article._id:
            raise tornado.web.HTTPError(500, 'slug %r exists', slug)

        return slug

    def _make_slug(self, article, source):
        source_slug = source.slug
        if source_slug is None:
            link = source.link
            source_slug = link.split('/')[-1]
            if (source_slug.endswith('.html') or
                    source_slug.endswith('.htm') or
                    source_slug.endswith('.asp')):
                source_slug = ''.join(slug.split('.')[:-1])

        if not Article(source_slug):
            return source_slug

        user_based_slug = '%s-%s' % (source_slug, self.current_user.name)
        if not Article(user_based_slug):
            return user_based_slug

        indexed_slug = user_based_slug + '-%s'
        index = 0
        while True:
            index += 1
            slug = indexed_slug % index
            if not Article(slug):
                return slug

    def save_for_normal(self, article, source):
        article.status = article.AWAIT
        article.save()

    def save_for_su(self, article, source):
        source.translated = article.slug
        article.status = article.ACCEPTED
        article.save()
        source.save()
        Article.eject_except(article.source['link'], article._id)
