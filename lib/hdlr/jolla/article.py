import tornado.web
import tornado.escape
import logging
import time
import json
try:
    from urllib.parse import unquote, quote, urlsplit
except ImportError:
    from urllib import quote
    from urlparse import unquote, urlsplit
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from .base import BaseHandler
import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db.jolla import Article, Author, User
from lib.tool import md
from lib.config import Config
sys.path.pop(0)

logger = logging.getLogger('jolla.article')

class ArticleHandler(BaseHandler):
    HOST = Config().main_host

    def get(self, slug):
        slug = unquote(slug)
        lang = self.locale.code[:2].lower()
        article = Article(slug, lang)
        if not article:
            raise tornado.web.HTTPError(404, "article %s not found" % slug)

        logger.info(article.author)

        return self.render(
            'jolla/article.html',
            article=article,
            md2html=md.md2html,
            escape=tornado.escape.xhtml_escape,
            make_source=self.make_source,
        )

    def formal(self, info):
        info = self.parse_db_data(info)
        self.parse_format(info)
        self.parse_time(info)
        return info

    def parse_db_data(self, info):
        result = {
            'title': info['zh']['title'],
            'author': info['author'],
            'tag': info['tag'],
            'content': info['zh']['content'],
            'original': None,
            'img': info['headimg'],
            'description': info['zh']['description'],
            'createtime': info['createtime'],
            'edittime': info['edittime'],
            'await': False,
            'reject': False,
            'id': str(info['_id'])
        }

        if info.get('transinfo', None):
            result['original'] = {
                'title': info['transinfo']['title'],
                'author': info['transinfo']['author'],
                'link': info['transinfo']['link'],
            }
            result['source'] = self.get_source_name(info['transinfo']['link'])
            result['await'] = info['transinfo']['status'] == Article.AWAIT
            result['reject'] = info['transinfo']['status'] == Article.REJECT
        else:
            result['source'] = None

        result['email'] = info['email'] if info['show_email'] else None

        return result

    def parse_time(self, info):
        info['content'] = md.md2html(info['content'])

        if info['description'] is not None:
            info['description'] = self.md_description_to_html(
                    info['description'])

    def parse_format(self, info):
        info['createtime'] = (
            time.strftime("%Y-%m-%d", time.localtime(info['createtime'])))
        info['edittime'] = (
            time.strftime("%Y-%m-%d", time.localtime(info['edittime'])))

    def original_author(self, name):
        meta = {
            'name': name,
            'photo': None,
            'intro': None
        }
        jolla_author = JollaAuthor(name)
        if not jolla_author.new:
            meta['photo'] = jolla_author.photo
            meta['intro'] = jolla_author.translation
        return meta

    def this_author(self, name):
        user = User(name)
        info = user.get()
        intro = info['intro']
        donate_info = info['donate']
        if not donate_info['show_in_article']:
            donate = None
        elif donate_info['info']:
            donate = donate_info['old']
        else:
            donate = donate_info['new']
        return {
            'name': name,
            'photo': info.get('img', None),
            'intro': intro['content'] if intro['show_in_article'] else None,
            'donate': donate
        }