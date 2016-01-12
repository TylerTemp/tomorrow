# coding: utf-8
# this file is to adjust the data in database

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db.tomorrow import Article, User, db
from lib.db.jolla import Article as JArticle, User as JUser, Author
sys.path.pop(0)

article = Article.collection

def fix_myself():
    print('fix myself')
    tyler = User('TylerTemp')
    assert tyler
    tyler.photo = tyler.__dict__['__info__'].pop('img')
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
    print(j_tyler._id)
    j_tyler.save()
    print(j_tyler._id)


def fix_jolla_author():
    jollas = db.jolla_author
    for each in jollas.find({}):
        j = Author(each['name'])
        j.photo = each['photo']
        j.introduce = each['translation']
        j.save()
    jollas.drop()


def fix_blog_article(art):
    art.pop('board')
    art.pop('title', None)
    art.pop('transinfo', None)
    art.pop('status', None)
    art.pop('index', None)
    art['create_time'] = art['createtime']
    art['edit_time'] = art['edittime']
    if 'headimg' in art:
        art['banner'] = art.pop('headimg')


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
    j_u = JUser.by_source_id(JUser.TOMORROW, tmr_id)
    return j_u._id


if __name__ == '__main__':
    JUser.collection.drop()
    JArticle.collection.drop()
    fix_jolla_author()
    fix_myself()
    my_id = get_my_id()
    print(my_id)
    for each in article.find({}):
        if 'board' not in each:
            continue

        if each['board'] == 'blog':
            # continue
            fix_blog_article(each)
            article.replace_one({'_id': each['_id']}, each)
        elif each['board'] == 'jolla':
            # continue
            fix_jolla_article(each, my_id)
        else:
            # continue
            article.delete_one({'_id': each['_id']})
            continue
