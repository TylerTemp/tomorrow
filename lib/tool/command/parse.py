"""
Usage:
    parse [options] <url> [<save-dir>]

Options:
"""

import logging
import os
from bs4 import BeautifulSoup
import requests
import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8000)
socket.socket = socks.socksocket

try:
    from urllib.request import urlretrieve
    from urllib.parse import urlparse
except ImportError:
    from urllib import urlretrieve, urlparse

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

    banner_img = body.find('img')
    banner = banner_img.get('src')
    a = banner_img.parent
    assert a.name == 'a'
    cover = a.get('href')
    logger.debug(banner)
    logger.debug(cover)
    result['banner'] = banner
    result['cover'] = cover
    result['imgs'] = imgs = []

    for each in body.find_all('img'):
        small = each.get('src')
        if small.endswith('favicon.png'):
            continue

        parent = each.parent
        if parent.name == 'a':
            big = parent.get('href')
            if big == 'javascript:;':
                big = None
        else:
            big = None

        imgs.append((small, big))

    result['author'] = 'Simo Ruoho'

    return result


def parse_jolla(url):
    soup = mk_soup(url)
    # with open('/tmp/save.html', 'r', encoding='utf-8') as f:
    #     soup = BeautifulSoup(f.read(), 'html5lib')
    #     # f.write(soup.prettify())

    result = {}

    img_div = soup.find(None, {'class': 'blog-img-wrap'})
    banner = img_div.find('img').get('src')
    logger.debug(banner)
    result['banner'] = banner

    tags = set()
    tags_tag = soup.find(None, {'class': 'blog-cats'})
    for a_tag in tags_tag.find_all('a'):
        tags.add(a_tag.text.lower().strip())
    logger.debug(tags)

    author = soup.find(None, {'class': 'author-name'}).text.strip()
    logger.debug(author)
    result['author'] = author

    blog = soup.find(None, {'class': 'blog-wrap'})
    title = blog.find('h1').text.strip()
    result['title'] = title

    imgs = []
    for img in blog.find_all('img'):
        small = img.get('src')
        parent = img.parent
        if parent.name == 'a':
            big = parent.get('href')
            if big == 'javascript:;':
                big = None
        else:
            big = None

        if small == big:
            small = None

        imgs.append((small, big))

    result['imgs'] = imgs

    result['cover'] = _find_jolla_cover(url)
    return result


def _find_jolla_cover(url):
    page = 1
    while True:
        if page == 1:
            url_page = 'https://blog.jolla.com/'
        else:
            url_page = 'https://blog.jolla.com/page/%s/' % page
        logger.debug('looking %s', url_page)

        resp = requests.get(url_page)
        if resp.status_code >= 400:
            logger.critical('%s not found', url_page)
            return None

        soup = mk_soup(url_page)
        for article in soup.find_all('article'):
            right = article.find(None, {'class': 'cont-right'})
            a_tag = right.find('a')
            href = a_tag.get('href')
            if href == url:
                return a_tag.find('img').get('src')

        page += 1


def save(dic, folder):
    url_to_path = []

    for key in ('cover', 'banner'):
        url = dic[key]
        if not url:
            continue
        ext = os.path.splitext(url)[-1]
        path = os.path.join(folder, key + ext)

        url_to_path.append((url, path))

    for small, big in dic['imgs']:

        if big and big not in (dic['cover'], dic['banner']):
            fname = _guess_fname(big)
            url_to_path.append((big, os.path.join(folder, fname)))

        if small and small not in (dic['cover'], dic['banner']):
            fname = _guess_fname(small)
            if big:
                big_name = _guess_fname(big)
                if big_name == fname:
                    parts = os.path.splitext(fname)
                    fname = '-small'.join(parts)

            url_to_path.append((small, os.path.join(folder, fname)))

    for url, path in url_to_path:
        logger.debug('%s -> %s', url, path)
        _fname, _headers = urlretrieve(url, path)
        logger.info(_fname)


def _guess_fname(url):
    parts = url.split('/')
    return parts[-1] if parts[-1] else parts[-2]


def parse(url):
    parsed = urlparse(url)
    netloc = parsed.netloc
    if netloc.startswith('blog.jolla.'):
        return parse_jolla(url)
    if netloc.startswith('reviewjolla.blogspot.'):
        return parse_reviewjolla(url)

    raise ValueError('%r not suport' % url)


if __name__ == '__main__':
    import docpie
    from pprint import pformat
    import os

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('docpie').setLevel(logging.CRITICAL)
    logging.getLogger('requests').setLevel(logging.CRITICAL)

    args = docpie.docpie(__doc__)
    url = args['<url>']
    result = parse(url)

    logger.info('\n' + pformat(result))

    save_dir = args['<save-dir>']
    if save_dir:
        save(result, os.path.expanduser(save_dir))
