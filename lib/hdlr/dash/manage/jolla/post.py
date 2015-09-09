import tornado.web
import logging
import json
from bson.objectid import ObjectId
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

import sys
import os
sys.path.insert(0, os.path.normpath(
                    os.path.join(__file__, '..', '..', '..', '..', '..')))
from lib.hdlr.dash.base import BaseHandler, ItsMyself
from lib.hdlr.base import EnsureUser
from lib.db import Article, Jolla, User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.manage.jolla.post')


class PostHandler(BaseHandler):

    @ItsMyself('manage/jolla/post/')
    @EnsureUser(level=User.admin, active=True)
    def get(self, user):
        self.xsrf_token
        id = self.get_argument('id', None)
        slug = self.get_argument('slug', None)
        if id is None and slug is None:
            return self.render_page()
        elif id:
            return self.get_info(id)
        elif slug:
            return self.get_article(slug)
        return self.render_page()

    def render_page(self):
        return self.render(
            'dash/manage/jolla/post.html',
            jolla=self.parse_jolla(),
            act=('manage', 'manage-jolla', 'manage-jolla-post')
        )

    def get_article(self, slug):
        article = Article(slug)
        assert not article.new, 'article %s not exists' % slug
        info = article.get()['zh']
        return self.write(json.dumps({'error': 0,
                                      'content': info['content'],
                                      'description': info['description']}))

    def parse_jolla(self):
        for each in Jolla.all():
            each['id'] = each.pop('_id')
            each['translated'] = each.pop('trusted_translation')
            each['trans_num'] = \
                Article.find_ref_number(each['slug'])
            yield each

    def get_info(self, id):
        info = Jolla.find_id(ObjectId(id))
        if info is None:
            raise tornado.web.HTTPError(404, 'id(%s) not exist' % id)
        result = {}
        link = info['link']
        result['link'] = link
        result['title'] = info['title']
        result['edit'] = '/jolla/task/%s/' % quote(info['slug'])
        prio = info.get('index', None)
        if prio is not None:
            prio = abs(prio)
        result['priority'] = prio
        trans_slug = info['trusted_translation']
        if trans_slug:
            article = Article(trans_slug)
            trans = article.get()
            d = trans['zh']
            result['trans_title'] = d['title']
            result['trans_link'] = '/jolla/blog/%s/' % quote(trans_slug)
            result['trans_author_name'] = trans['author']
            result['trans_author_link'] = '/hi/%s/' % quote(trans['author'])
            result['trans_content'] = d['content']
            result['trans_description'] = d['description']

        result['trans'] = collect = []
        for each in Article.find_ref(info['slug']):
            collect.append({'title': each['zh']['title'],
                            'author': each['author'],
                            'slug': each['slug']})

        self.write(json.dumps(result))
        self.finish()

        if trans_slug and info.get('index', None) != trans['index']:
            logger.info('incorrect index %s of %s, fix to %s',
                        trans['index'],
                        trans['slug'],
                        result['priority'])
            trans['index'] = result['priority']
            article.save()

    @ItsMyself('manage/jolla/')
    @EnsureUser(level=User.admin, active=True)
    def post(self, user):
        self.check_xsrf_cookie()

        index = self.get_argument('prority', None) or None
        if index:
            index = -abs(int(index))
        _id = ObjectId(self.get_argument('id'))

        logger.debug('manage jolla id %s', _id)

        jolla = Jolla()
        jolla.set(Jolla.find_id(_id))
        jolla_info = jolla.get()

        slug = self.get_argument('slug', None)
        if not slug:
            trusted = jolla_info['trusted_translation']
            if trusted:
                jolla_info['trusted_translation'] = None
                article = Article(trusted)
                article_info = article.get()
                article_info['transinfo']['status'] = Article.AWAIT
                article.save()
                logger.info('untrust %s', jolla_info['slug'])
        else:
            article = Article(slug)
            assert not article.new, 'article %s should not be new' % slug
            content = self.get_argument('content')
            assert content, 'content should never be empty'
            description = self.get_argument('description', '').strip() or None
            article_info = article.get()
            article_info['zh']['content'] = content
            article_info['zh']['description'] = description
            article_info['index'] = index
            article_info['transinfo']['status'] = Article.TRUSTED
            jolla_info['trusted_translation'] = article_info['slug']
            article.save()
        self.write(json.dumps({'error': 0}))
        self.finish()

        if index != jolla_info['index']:
            jolla_info['index'] = index
            coll = Article.get_collect()
            result = coll.update_many(
                {'board': 'jolla', 'transinfo.slug': jolla_info['slug']},
                {'$set': {'index': index}})
            logger.debug('updated %s translation', result.modified_count)
            # for each in Article.
        jolla.save()
