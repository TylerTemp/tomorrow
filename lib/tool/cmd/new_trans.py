"""
Usage:
    new_trans [options] <url>

Options:
    -u, --user=<user>
    -p, --pwd=<pwd>
    -k, --key=<key>
    -s, --secret=<secret>
    --slug=<slug>
    -c, --cover=<cover>
    -l, --local
"""

import os
import json
import docpie
import logging
import requests
from login import login_jolla
from parse import parse
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

args = docpie.docpie(__doc__)

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('docpie').setLevel(logging.CRITICAL)
logger.setLevel(logging.DEBUG)

with open(os.path.normpath(os.path.join(__file__, '..', 'config.conf')),
          'r',
          encoding='utf-8') as f:
    config = json.load(f)

# login
user = args['--user'] or config['user']
pwd = args['--pwd'] or config['pwd']
if args['--local']:
    jolla_base = 'https://jolla.fake.today/'
    tomorrow_base = 'https://tomorrow.fake.today/'
else:
    jolla_base = 'https://jolla.come.today/'
    tomorrow_base = 'https://tomorrow.come.today/'

session = login_jolla(user, pwd, jolla_base, tomorrow_base)

# parse article
article_url = args['<url>']
logger.info(article_url)
article_meta = parse(article_url)
logger.info(article_meta)

