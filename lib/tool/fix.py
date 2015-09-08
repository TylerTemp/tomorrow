# coding: utf-8
# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote, quote
from pprint import pprint

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import Article, Jolla
sys.path.pop(0)

coll = Article._article
joll = Jolla._jolla

a = coll.find_one({'url': 'Developer-spotlight:-Siteshwar-on-open-source-and-Sailfish-Browser'})
j = joll.find_one({'url': 'Developer-spotlight:-Siteshwar-on-open-source-and-Sailfish-Browser'})
a['cover'] = 'https://dn-jolla.qbox.me/private_browsing_huechange_1-640x480.png'
a['headimg'] = 'https://dn-jolla.qbox.me/private_browsing_huechange_wide-1024x480.png'
j['cover'] = 'https://dn-jolla.qbox.me/private_browsing_huechange_1-640x480.png'
j['headimg'] = 'https://dn-jolla.qbox.me/private_browsing_huechange_wide-1024x480.png'

coll.save(a)
joll.save(j)

a = coll.find_one({'url': 'Jolla-Tablet-and-the-New-UI'})
j = joll.find_one({'url': 'Jolla-Tablet-and-the-New-UI'})
result = 'http://' + a['transinfo']['link']
a['transinfo']['link'] = result
j['link'] = result

coll.replace_one({'_id': a['_id']}, a)
joll.replace_one({'_id': j['_id']}, j)

a = coll.find_one({'url': 'Sailfish-OS-update-Äijänpäivänjärvi-now-available-for-everyone!'})
j = joll.find_one({'url': 'Sailfish-OS-update-Äijänpäivänjärvi-now-available-for-everyone!'})

a['cover'] = 'https://dn-jolla.qbox.me/osu201504_tw640480_pien.jpg'
j['cover'] = 'https://dn-jolla.qbox.me/osu201504_tw640480_pien.jpg'

coll.save(a)
joll.save(j)

a = coll.find_one({'url': 'Jolla-Communicator:-An-Easy-Way-to-Communicate-between-Ubuntu-Desktop,-Fedora,-Arch-&-Sailfish-OS'})
j = joll.find_one({'url': 'Jolla-Communicator:-An-Easy-Way-to-Communicate-between-Ubuntu-Desktop,-Fedora,-Arch-&-Sailfish-OS'})

a['cover'] = 'https://dn-jolla.qbox.me/Jolla_red-262x164.jpg'
j['cover'] = 'https://dn-jolla.qbox.me/Jolla_red-262x164.jpg'

coll.save(a)
joll.save(j)

a = coll.find_one({'url': 'Jolla-Tablet-and-the-New-UI'})
j = joll.find_one({'url': 'Jolla-Tablet-and-the-New-UI'})

a['cover'] = 'https://dn-jolla.qbox.me/IMG_2613-262x197.jpg'
j['cover'] = 'https://dn-jolla.qbox.me/IMG_2613-262x197.jpg'

coll.save(a)
joll.save(j)


for each in coll.find({'board': 'jolla'}):
    if 'transinfo' not in each:
        continue
    dir_cover = each.get('cover')
    info_cover = each['transinfo'].get('cover', None)

    dir_headimg = each.get('headimg')
    info_headimg = each['transinfo'].get('headimg', None)


    each['transinfo'].pop('headimg', None)
    each['transinfo'].pop('cover', None)
    each['headimg'] = dir_headimg or info_headimg
    each['cover'] = dir_cover or info_cover
    each['tag'] = []
    each['description'] = None
    each.pop('license', None)
    each.pop('transref', None)
    coll.replace_one({'_id': each['_id']}, each)

for each in coll.find({}):
    if 'url' in each:
        each['slug'] = each.pop('url')
    each.pop('transref', None)
    if 'transinfo' in each:
        each['transinfo']['slug'] = each['transinfo'].pop('url')

    if 'zh' not in each:
        each['zh'] = {
            'title': each.pop('title'),
            'content': each.pop('content'),
            'description': each.pop('description')
        }
    coll.replace_one({'_id': each['_id']}, each)

for each in joll.find({}):
    if 'url' in each:
        each['slug'] = each.pop('url')
    each['tag'] = []
    joll.replace_one({'_id': each['_id']}, each)
