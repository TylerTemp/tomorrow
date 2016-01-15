import tornado.web
import tornado.gen
import logging
import json
try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote
    from urlparse import unquote

from .base import BaseHandler
from lib.tool.md import html2md
from lib.tool.md import escape
from lib.db.jolla import Article, User, Source

logger = logging.getLogger('tomorrow.jolla.translate')


class TranslateHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
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

        title = self.get_argument('title')
        format = self.get_argument('format')
        content = self.get_argument('content')
        show_email = self.get_argument('show_email', True)
        description = self.get_argument('description', '').strip() or None

        slug = unquote(slug)
        to_translate = Jolla(slug)
        if to_translate.new:
            raise tornado.web.HTTPError(
                404,
                "the article to translate not found: %s", slug)

        user_info = self.get_current_user()

        if format != 'md':
            content = html2md(content)
        elif self.current_user['type'] < User.root:
            content = escape(content)

        to_trans_info = to_translate.get()
        trans_info = {
            'board': 'jolla',
            'zh': {
                'title': title,
                'content': content,
                'description': description,
            },
            'author': user_info['user'],
            'email': user_info['email'],
            'show_email': show_email,
            'headimg': to_trans_info['headimg'],
            'cover': to_trans_info.get('cover', None),
            'tag': to_trans_info['tag'],
            'transinfo': {
                'link': to_trans_info['link'],
                'author': to_trans_info['author'],
                'slug': to_trans_info['slug'],
                'title': to_trans_info['title'],
                'status': Article.AWAIT,
            }
        }

        translated = Article()
        translated_info = translated.find_trans_slug_translator(
            slug, user_info['user'])

        if translated_info is None:
            translated.add(**trans_info)
            logger.info('New translate %s', to_trans_info['slug'])
        else:
            translated_info.update(trans_info)
            translated.set(translated_info)
            translated_info = translated.get()
            logger.info('Renew translate %s', translated_info['slug'])
        translated_info = translated.get()

        this_slug = translated_info['slug']
        old_slug = to_trans_info['trusted_translation']
        logger.debug('old: %s, new: %s', old_slug, this_slug)
        if old_slug is None and user_info['type'] >= User.admin:
            if this_slug != to_trans_info['slug']:
                conflicting_article = Article(to_trans_info['slug'])
                if not conflicting_article.new:
                    con_info = conflicting_article.get()
                    con_title = con_info['zh']['title']
                    con_author = con_info['author']
                    con_info['slug'] = conflicting_article.mkslug(
                        con_title, con_author)
                    conflicting_article.save()
                translated_info['slug'] = to_trans_info['slug']
                this_slug = to_trans_info['slug']

            logger.debug(
                'trust %s as translation of %s',
                translated_info['slug'], old_slug)

            to_trans_info['trusted_translation'] = translated_info['slug']
            translated_info['transinfo']['status'] = translated.TRUSTED
            to_translate.save()
        elif old_slug == this_slug:
            translated_info['transinfo']['status'] = translated.TRUSTED
        else:
            translated_info['transinfo']['status'] = translated.AWAIT
        translated_info['index'] = to_trans_info['index']

        translated.save()

        result = {
            'error': 0,
            'redirect': 'http://%s/%s/' % (self.config.jolla_host, this_slug),
        }

        return self.write(json.dumps(result))
