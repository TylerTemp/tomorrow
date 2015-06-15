# this file is to adjust the data in database

import sys
import os

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import db
sys.path.pop(0)

article = db.article
jolla  = db.jolla

for each in article.find({}):
    each['index'] = 0
    article.save(each)

for each in jolla.find({}):
    each['index'] = 0
    jolla.save(each)
