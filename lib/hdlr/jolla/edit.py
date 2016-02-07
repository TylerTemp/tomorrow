import tornado.web
import tornado.escape
import logging
import json
try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote
    from urlparse import unquote

from .base import BaseHandler
from lib.tool.md import md2html
from lib.tool.md import escape
from lib.db.jolla import Article, User, Source, Redirect


class EditHandler(BaseHandler):
    logger = logging.getLogger('jolla.translate')

    @tornado.web.authenticated
    def get(self, slug=None):
        if self.get_argument('action', None) == 'preview':
            return self.preview()
        if slug is not None:
            slug = unquote(slug)
        article = self.get_article(slug)
        self.debug(article.lang)

        return self.render(
            'jolla/edit.html',
            article=article
        )

    @tornado.web.authenticated
    def post(self, slug=None):
        if self.get_argument('action', None) == 'preview':
            return self.preview()
        if slug is not None:
            slug = unquote(slug)
        article = self.get_article(slug)
        new_slug = self.get_argument('slug')
        if slug != new_slug:
            if Article(new_slug) or Redirect(new_slug):
                raise tornado.web.HTTPError(500, 'slug %r exists' % new_slug)
        self.fill_article(article)
        self.assert_article(article)
        user = self.current_user
        if not article.author:
            article.author = user._id
        if user.type >= user.ROOT:
            article.status = article.ACCEPTED

        article.save()
        return self.write(json.dumps({'error': 0,
                                      'redirect': '//%s/%s/' % (
                                          self.config.jolla_host, article.slug)}))

    def get_article(self, slug):
        lang = self.get_argument('source', 'zh')
        if slug is None:
            return Article(lang=lang)

        article = Article(unquote(slug), lang=lang)
        if not article:
            raise tornado.web.HTTPError(
                404, 'post %r not found' % unquote(slug))

        user = self.current_user
        if article and article.author != user.name and user.type < user.ROOT:
            raise tornado.web.HTTPError(
                500, 'No right to edit %r' % unquote(slug))

        return article

    def preview(self):
        article = Article()
        self.fill_article(article)
        content = article.content or ''
        if article.description:
            desc = md2html(article.description)
        else:
            desc = tornado.escape.xhtml_escape(content[:100])
        content = md2html(content)
        return self.write(json.dumps({'description': desc,
                                      'content': content}))

    def fill_article(self, article):
        article.title = self.get_argument('title', '').strip() or None
        article.description = (self.get_argument('description', '').strip() or
                               None)
        article.content = self.get_argument('content', '').strip() or None
        article.banner = self.get_argument('banner', '').strip() or None
        article.cover = self.get_argument('cover', '').strip() or None
        article.slug = self.get_argument('slug', '').strip() or None

        tag = []
        for each in self.get_argument('tag', '').split(','):
            t = each.strip()
            if t:
                tag.append(t)
        article.tag = tag

    def assert_article(self, article):
        if not (article.title and article.slug):
            raise tornado.web.MissingArgumentError('title' if article.slug
                                                   else 'slug')