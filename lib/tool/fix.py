# coding: utf-8
# this file is to adjust the data in database

import logging
import pymongo
import sys
import os
import json

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db.tomorrow import Article, User, db, Auth
from lib.db.jolla import Article as JArticle, User as JUser, Author, Source
from lib.db.base import Meta
from lib.config.jolla import Config as JConfig
sys.path.pop(0)

article = Article.collection
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def fix_jolla_app():
    config = JConfig()
    jolla_app = config.tomorrow
    auth = Auth(jolla_app['key'])
    auth.secret = jolla_app['secret']
    auth.name = 'Jolla中文博客'
    auth.callback = jolla_app['callback']
    auth.save()


def fix_myself():
    old_tyler = User.collection.find_one({'user': 'TylerTemp'})
    tyler = User()
    tyler.photo = old_tyler.pop('img')
    tyler.name = old_tyler.pop('user')
    tyler.update(old_tyler)
    assert tyler
    old_intro = tyler.intro
    old_intro['zh'] = old_intro.pop('content')
    old_donate = tyler.donate
    old_donate['zh'] = old_donate.pop('new')
    old_donate.pop('old')
    old_donate.pop('info')
    tyler.save()
    tyler_tomorrow_id = tyler._id
    j_tyler = JUser()
    j_tyler.source = j_tyler.TOMORROW
    j_tyler.uid = tyler_tomorrow_id
    j_tyler.email = tyler.email
    j_tyler.home = 'https://tomorrow.comes.today/hi/TylerTemp/'
    j_tyler.name = 'TylerTemp'
    j_tyler.photo = tyler.photo
    j_tyler.intro = tyler.intro['zh']
    j_tyler.donate = tyler.donate['zh']
    j_tyler.type = j_tyler.ROOT
    logger.debug(j_tyler._id)
    j_tyler.save()


def fix_jolla_author():
    jollas = db.jolla_author
    for each in jollas.find({}):
        j = Author(each['name'])
        j.photo = each['photo']
        j.intro = each['translation']
        j.save()
    jollas.drop()


def fix_blog_article(art):
    art.pop('board')
    art.pop('title', None)
    art.pop('transinfo', None)
    art.pop('status', None)
    art.pop('index', None)
    art.pop('verify', None)
    art['create_time'] = art.pop('createtime')
    art['edit_time'] = art.pop('edittime')
    if 'headimg' in art:
        art['banner'] = art.pop('headimg')
    article.replace_one({'_id': art['_id']}, art)


def fix_jolla_article(art, translator_id):
    if 'headimg' in art:
        art['banner'] = art.pop('headimg')

    jr = JArticle(art['slug'], 'zh')
    jr.content = art['zh']['content']
    jr.description = art['zh']['description']
    jr.title = art['zh']['title']
    jr.status = jr.ACCEPTED
    jr.create_time = art.get('create_time', None) or art['createtime']
    jr.edit_time = art.get('edit_time', None) or art['edittime']
    jr.cover = art['cover']
    jr.banner = art['banner']
    jr.tag = art['tag']
    jr.author = translator_id
    if 'transinfo' in art:
        jr.source = {'link': art['transinfo']['link'],
                     'author': art['transinfo']['author'],
                     'title': art['transinfo']['title']}
    jr.save()
    article.delete_one({'_id': art['_id']})

def get_my_id():
    tmr_u = User('TylerTemp')
    tmr_id = tmr_u._id
    logger.debug('tmr id %s', tmr_id)
    j_u = JUser.by_source_id(JUser.TOMORROW, tmr_id)
    return j_u._id


def fix_jolla_source():
    old_source = db.jolla.find({}).sort(
            (('index', pymongo.ASCENDING),
             ('createtime', pymongo.DESCENDING)
            ))
    for old in old_source:
        s = Source(old['link'])
        s.title = old['title']
        s.author = old['author']
        s.banner = old['headimg']
        s.cover = old['cover']
        s.create_time = old['createtime']
        s.tag = old['tag']
        s.translated = old['trusted_translation']
        s.save()
        db.jolla.delete_one({'_id': old['_id']})


def fix_for_brey(art):
    # print('-' * 35)
    # for k, v in art.items():
    #     print(k, v if k != 'en' else '--')
    # print('-' * 35)
    meta = Meta(art['slug'][5:], 'brey')
    _article = art['en']
    meta.title = _article['title']
    meta.content = _article['content']
    meta.slug = art['slug'][5:]
    logger.debug('%s - %s', meta.slug, meta.title)
    meta.save()
    Article.collection.delete_one({'_id': art['_id']})

def fix_docpie_example(art):
    edit_time = art['edittime']
    examples = json.loads(art['en']['content'])
    examples['edit_time'] = edit_time
    examples['myscript_py'] = examples.pop('myscript.py')
    examples['mycopy_py'] = examples.pop('mycopy.py')
    meta = Meta('examples', 'docpie')
    meta.__dict__['__info__'].update(examples)
    meta.save()
    Article.collection.delete_one({'_id': art['_id']})


def fix_docpie_home(art):
    meta = Meta('home', 'docpie')
    art['en'].pop('description', None)
    art['zh'].pop('description', None)
    meta.en = art['en']
    meta.zh = art['zh']
    meta.save()
    Article.collection.delete_one({'_id': art['_id']})


def fix_docpie_doc(art):
    meta = Meta(art['slug'], 'docpie')
    zh = art['zh']
    meta.zh = {'content': zh['content'].replace('?example=myscript.py', '?example=myscript_py').replace('?example=mycopy.py', '?example=mycopy_py'), 'title': zh['title']}
    en = art['en']
    meta.en = {'content': en['content'].replace('?example=myscript.py', '?example=myscript_py').replace('?example=mycopy.py', '?example=mycopy_py'), 'title': en['title']}
    meta.save()
    Article.collection.delete_one({'_id': art['_id']})

if __name__ == '__main__':
    JUser.collection.drop()
    JArticle.collection.drop()
    Author.collection.drop()
    Meta.collection.drop()
    fix_jolla_source()
    fix_jolla_app()
    fix_jolla_author()
    fix_myself()
    my_id = get_my_id()
    logger.debug(my_id)
    for each in article.find({}):

        if each['board'] == 'blog':
            # continue
            fix_blog_article(each)

        elif each['board'] == 'jolla':
            # continue
            fix_jolla_article(each, my_id)
        elif each['slug'].startswith('brey'):
            # continue
            fix_for_brey(each)
        elif each['slug'] == 'docpie-example':
            fix_docpie_example(each)
        elif each['slug'] == 'docpie_home':
            fix_docpie_home(each)
        elif each['slug'] == 'experimental-apis' or 'docpie' in each['tag']:
            fix_docpie_doc(each)
        else:
            logger.warning(each['slug'] + '!!!!!!!!!!!')

            article.delete_one({'_id': each['_id']})