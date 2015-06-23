import tornado.web
import tornado.gen
import logging
import json
import re
try:
    from urllib.parse import quote
    from urllib.parse import unquote
except ImportError:
    from urlparse import quote
    from urlparse import unquote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.tool.md import md2html
from lib.tool.md import html2md
from lib.tool.md import escape
from lib.hdlr.base import EnsureUser
from lib.tool.minsix import py3
from lib.db import Jolla
from lib.db import Article
from lib.db import User
from lib.config import Config
sys.path.pop(0)

cfg = Config()
logger = logging.getLogger('tomorrow.jolla.translate')


class TranslateHandler(BaseHandler):

    @EnsureUser(level=User.normal, active=True)
    def get(self, url):
        url = unquote(url)
        to_translate = Jolla.find_url(url)
        if to_translate is None:
            raise tornado.web.HTTPError(404,
                                        "the article to translate not found")

        self.xsrf_token

        translate = {
            'title': to_translate['title'],
            'md': to_translate['content'],
            'html': md2html(to_translate['content']),
        }

        userinfo = self.get_current_user()

        username = userinfo['user']
        usertype = userinfo['type']
        translated = Article.find_ref_of_user(url, username)
        imgs, files = self.get_imgs_and_files(username, usertype)
        if usertype >= User.admin:
            edit_task_url = '/jolla/task/' + quote(url)
        else:
            edit_task_url = None

        if translated is None:
            translated = {k: '' for k in translate.keys()}
            translated['reprint'] = {}
        else:
            translated = {
                'title': translated['title'],
                'md': translated['content'],
                'html':md2html(translated['content']),
                'reprint': translated['transinfo']['reprint'],
            }

        return self.render(
            'jolla/translate.html',
            translate=translate,
            translated=translated,
            user=username,
            imgs=imgs,
            files=files,
            edit_task_url=edit_task_url,
            img_upload_url=('/hi/%s/img/' % quote(username)
                            if username else None),
            file_upload_url=('/hi/%s/file/' % quote(username)
                             if username else None),
            size_limit=cfg.size_limit.get(usertype, 0),
            md=self.get_argument('md', False),
        )

    # @tornado.web.asynchronous
    # @tornado.gen.coroutine
    @EnsureUser(level=User.normal, active=True)
    def post(self, url):
        self.check_xsrf_cookie()

        title = self.get_argument('title')
        format = self.get_argument('format')
        content = self.get_argument('content')
        show_email = self.get_argument('show_email', True)
        reprint = self.get_reprint_argument()

        url = unquote(url)
        to_translate = Jolla(url)
        if to_translate.new:
            raise tornado.web.HTTPError(
                404,
                "the article to translate not found: %s", url)

        user_info = self.get_current_user()

        if format != 'md':
            content = html2md(content)
        elif self.current_user['type'] < User.root:
            content = escape(content)

        to_trans_info = to_translate.get()
        trans_info = {
            'board': 'jolla',
            'title': title,
            'content': content,
            'author': user_info['user'],
            'email': user_info['email'],
            'show_email': show_email,
            'transinfo': {
                'link': to_trans_info['link'],
                'author': to_trans_info['author'],
                'url': to_trans_info['url'],
                'title': to_trans_info['title'],
                'headimg': to_trans_info['headimg'],
                'status': Article.AWAIT,
            }
        }

        translated = Article()
        translated_info = translated.find_trans_url_translator(
            url, user_info['user'])

        if translated_info is None:
            translated.add(**trans_info)
            logger.info('New translate %s', to_trans_info['url'])
        else:
            translated_info.update(trans_info)
            translated.set(translated_info)
            translated_info = translated.get()
            logger.info('Renew translate %s', translated_info['url'])
        translated_info = translated.get()
        translated_info['transinfo']['reprint'] = reprint
        logger.debug(translated_info['transinfo']['reprint'])

        this_url = translated_info['url']
        old_url = to_trans_info['trusted_translation']
        logger.debug('old: %s, new: %s', old_url, this_url)
        if old_url is None and user_info['type'] >= User.admin:
            if this_url != to_trans_info['url']:
                conflicting_article = Article(to_trans_info['url'])
                if not conflicting_article.new:
                    con_info = conflicting_article.get()
                    con_title = con_info['title']
                    con_author = con_info['author']
                    con_info['url'] = conflicting_article.mkurl(
                        con_title, con_author)
                    conflicting_article.save()
                translated_info['url'] = to_trans_info['url']
                this_url = to_trans_info['url']

            logger.debug(
                'trust %s as translation of %s',
                translated_info['url'], old_url)

            to_trans_info['trusted_translation'] = translated_info['url']
            translated_info['transinfo']['status'] = translated.TRUSTED
            to_translate.save()
        elif old_url == this_url:
            translated_info['transinfo']['status'] = translated.TRUSTED
        else:
            translated_info['transinfo']['status'] = translated.AWAIT
        translated_info['index'] = to_trans_info['index']

        translated.save()

        result = {
            'error': 0,
            'redirect': '/jolla/blog/' + this_url,
        }

        return self.write(json.dumps(result))

    re_reprint = re.compile(r'^reprint\[(?P<key>.*?)\]$')
    def get_reprint_argument(self):
        result = {}
        re_reprint = self.re_reprint
        for k, v in self.request.arguments.items():
            match = re_reprint.match(k)
            if match is not None:
                if isinstance(v, (list, tuple)):
                    v = v[0]
                if py3:
                    v = v.decode('utf-8')
                result[match.groupdict()['key']] = v
        return result
