# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import db
sys.path.pop(0)

article = db.article
jolla  = db.jolla

slug = 'A-Peek-at-our-Ambience-Pic-Picks'
j = jolla.find_one({'url': slug})
a = article.find_one({'url': slug})
print(a['title'])
j['trusted_translation'] = a['url']
jolla.save(j)
