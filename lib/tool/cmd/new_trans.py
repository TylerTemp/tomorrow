"""
Usage:
    new_trans.py [options] parse <url>
    new_trans.py [options] <url>

Options:
    --save=<dir>
    -d, --dry-run
    -c, --cover=<img>
    -b, --banner=<img>
    -u, --user=<user>
    -p, --pwd=<pwd>
    -s, --slug=<slug>
"""

import logging
from bs4 import BeautifulSoup
import requests
from login import login_jolla

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

logger = logging.getLogger('new_trans')


def mk_soup(url):
    resp = requests.get(url)
    return BeautifulSoup(resp.content, 'html5lib')


def parse_reviewjolla(url):
    soup = mk_soup(url)
    # with open('/tmp/save.html', 'r', encoding='utf-8') as f:
    #     soup = BeautifulSoup(f.read(), 'html5lib')
    result = {}

    title = soup.find(None, {'class': 'post-title'}).text.strip()
    logger.debug(title)
    result['title'] = title

    body = soup.find(None, {'class': 'post-body'})
    # logger.debug(body.text)

    h2_tag = body.find('h2')
    banner = h2_tag.find('img').get('src')
    cover = h2_tag.find('a').get('href')
    logger.debug(banner)
    logger.debug(cover)
    result['banner'] = banner
    result['cover'] = cover
    result['imgs'] = imgs = []

    for each in body.find_all('img'):
        small = each.get('src')
        if small.endswith('favicon.png'):
            continue

        big = each.parent.get('href')
        if big == 'javascript:;':
            big = None
        imgs.append((small, big))

    return result


if __name__ == '__main__':
    from pprint import pprint
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('docpie').setLevel(logging.CRITICAL)

    url = 'http://reviewjolla.blogspot.sg/2016/03/follow-up-promise-on-sailfish-os-in.html'
    pprint(parse_reviewjolla(url))
