'''remove some personal information
run this directly bebore git add/push'''

import json
import os
import sys

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.tool.minsix import open
sys.path.pop(0)

conffile = os.path.join(rootdir, 'config.conf')
with open(conffile, 'r+', encoding='utf-8') as f:
    obj = json.load(f)
    obj.pop('mail', None)
    f.seek(0)
    f.truncate()
    json.dump(obj, f, indent=4)
