# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import db
sys.path.pop(0)

jolla = db.jolla

for each in jolla.find({}):
    if each.get('trusted_translation', None):
        continue
    old = each['url']
    link = each['link']
    listed = link.split('/')
    last = False
    while not last and listed:
        last = listed.pop(-1)
    print(old, '->', last)
    each['url'] = last
    jolla.save(each)
