# coding: utf-8
import tornado.web
import logging
import json
import time
import re
from bson.objectid import ObjectId
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

from lib.db import Article, Jolla
from lib.tool.md import md2html
from lib.config import Config
from .base import BaseHandler, ItsMyself

logger = logging.getLogger('tomorrow.dash.secure')


class ArticleHandler(BaseHandler):
    JOLLA_HOST = Config().jolla_host

    @tornado.web.authenticated
    @ItsMyself('article/')
    def get(self, user):

        return self.render(
            'tomorrow/admin/dash/article.html',
            articles=self.get_articles(self.current_user['user']),
            md2html=self.md2html,
            xsrf_token=self.xsrf_token,
        )

    @tornado.web.authenticated
    @ItsMyself('article/')
    def post(self, user):
        self.check_xsrf_cookie()

        coll = Article.get_collect()
        id_obj = ObjectId(self.get_argument('id'))
        arti_info = coll.find_one({'_id': id_obj})
        if not arti_info:
            self.clear()
            self.set_status(404)
            self.write(
                json.dumps({'msg': 'article id %s not exists' % id_obj}))
            return

        lang = self.get_argument('language', None)

        full_delete = False
        if ('transinfo' in arti_info and
                arti_info['transinfo']['status'] == Article.TRUSTED):
            jolla_url = arti_info['transinfo']['slug']
            jolla_post = Jolla(jolla_url)
            assert not jolla_post.new, 'Jolla(%s) not exists' % jolla_url
            jolla_info = jolla_post.get()
            logger.info('remove jolla trusted translation %s',
                        jolla_info['slug'])
            jolla_info['trusted_translation'] = None
            logger.info('remove article %s', arti_info['slug'])
            jolla_post.save()
            coll.delete_one({'_id': id_obj})
            full_delete = True
        else:
            assert lang is not None
            if lang not in arti_info:
                self.clear()
                self.set_status(404)
                self.write(
                    json.dumps(
                        {'msg': 'lang %s for %s not exists' % (lang, id_obj)}))
                return
            logger.info(
                'remove article %s language %s', arti_info['slug'], lang)
            arti_info.pop(lang)
            if 'en' not in arti_info and 'zh' not in arti_info:
                logger.info('remove article %s', arti_info['slug'])
                coll.delete_one({'_id': id_obj})
                full_delete = True

        return self.write(json.dumps({'full_delete': full_delete}))

    def get_articles(self, user):
        for each in Article.find_by(user):
            if 'zh' in each and 'en' in each:
                if self.locale.code[:2] != 'zh':
                    meta = each['en']
                else:
                    meta = each['zh']
            else:
                meta = each.get('zh', None) or each['en']

            each['id'] = str(each.pop('_id'))
            each['edit_time'] = self.format_time(each.pop('edittime'))
            each['create_time'] = self.format_time(each.pop('createtime'))
            if each['board'] == 'jolla':
                each['url'] = '//%s/%s/' % (self.JOLLA_HOST, each['slug'])
            else:
                each['url'] = '/blog/%s/' % each['slug']

            if 'transinfo' in each:
                each['edit'] = \
                    '/jolla/translate/%s/' % each['transinfo']['slug']
                each['source_title'] = each['transinfo']['title']
                each['source_url'] = each['transinfo']['link']
            else:
                each['edit'] = '/edit/%s/' % each['slug']
                each['lang'] = {
                    'zh': 'zh' in each,
                    'en': 'en' in each
                }
            each.update(meta)
            yield each

    def format_time(self, t):
        if self.locale.code.startswith('en'):
            return time.ctime(t)
        return time.strftime('%Y年%m月%d日，%H:%M', time.localtime(t))

    p_re = re.compile(r'^<p>.*?</p>$')

    def md2html(self, text):
        trans = md2html(text)
        if self.p_re.match(trans):
            trans = trans[3:-4]

        return trans
