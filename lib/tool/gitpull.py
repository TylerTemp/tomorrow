'''`git checkout .`
`git pull`
and add personal information back'''

import subprocess as sp
import json
import os
import sys

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))

sys.path.insert(0, rootdir)
from lib.tool.minsix import open
sys.path.pop(0)

if len(sys.argv) > 1 and sys.argv[1] == 'pull':
    sp.check_call(['git', 'checkout', '.'])
    sp.check_call(['git', 'pull'])

with open(os.path.join(rootdir, 'config.conf'), 'r+', encoding='utf-8') as f:
    obj = json.load(f)
    obj['mail'] = {
        "zh_CN": {
            "url": "mail.qq.com",
            "host": "smtp.qq.com",
            "user": "huang.exe@qq.com",
            "password": "CaoNiMa"
        },
        "default": {
            "url": "mail.google.com",
            "host": "smtp.gmail.com",
            "user": "tylertempdev@gmail.com",
            "password": "Huang123"
        }
    }
    f.seek(0)
    f.truncate()
    json.dump(obj, f, indent=4)
