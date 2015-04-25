import tornado.web
import tornado.httpclient
import tornado.gen
import logging
import json
from bs4 import BeautifulSoup
from bs4 import NavigableString
try:
    from urllib.parse import urlsplit
    from urllib.parse import urlunsplit
    from urllib.request import urlopen
except ImportError:
    from urlparse import urlsplit
    from urlparse import urlunsplit
    from urllib2 import urlopen

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.tool.md import html2md
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.load')


class LoadHandler(BaseHandler):
    SUPPORTED_HOST = (
        'blog.jolla.com',
        'www.jollausers.com',
        'www.jollatides.com',
    )

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        url = self.get_argument('url')
        host = self.host(url)
        if host not in self.SUPPORTED_HOST:
            logger.debug("not support %s", url)
            self.write(json.dumps({'error': 1}))
            return self.finish()

        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, url)
        body = response.body
        soup = BeautifulSoup(body)

        for img in soup.find_all('img'):
            self.fix_img(img, url)

        if host == 'blog.jolla.com':
            func = self.parse_jollablog
        elif host == 'www.jollausers.com':
            func = self.parse_jollausers
        elif host == 'www.jollatides.com':
            func = self.parse_jollatides
        else:
            self.write(json.dumps({'error': 1}))
            return self.finish()

        result = func(soup)
        result['error'] = 0
        self.write(json.dumps(result))
        self.finish()

    post = get

    @staticmethod
    def host(url):
        return urlsplit(url).netloc

    @classmethod
    def parse_jollablog(cls, soup):
        author = soup.find(True, {'class': 'author-name'}).string.strip()
        article = soup.article
        headimg = article.img['src']
        title = article.h1.string.strip()
        content = article.find('div', {'class': 'entry-content'})
        content.find(True, {'class': 'ssba'}).extract()
        mdcontent = html2md(str(content))
        htmlcontent = md2html(mdcontent)
        return dict(title=title, author=author,
                    headimg=headimg, md=mdcontent,
                    html=htmlcontent)

    @classmethod
    def parse_jollausers(cls, soup):
        title = soup.find('h1', {'class': 'post-title'}).string.strip()
        author = soup.find('div', {'class': 'sidebar-post'}).h5.string.strip()
        article = soup.article
        headimg = article.img['src']
        content = article.find('div', id='article')
        content.find(True, {'class': 'sharedaddy'}).extract()
        mdcontent = html2md(str(content))
        htmlcontent = md2html(mdcontent)

        return {
            'title': title,
            'author': author,
            'headimg': headimg,
            'md': mdcontent,
            'html': htmlcontent,
        }

    @classmethod
    def parse_jollatides(cls, soup):
        article = soup.find('div', {'class': 'post-content'})
        title = article.h2.string.strip()
        author = article.find('span', {'class': 'author'}).get_text()

        article.find(True, {'class': 'postitle'}).extract()
        article.find(True, id='fcbk_share').extract()
        article.find(True, {'class': 'single-metainfo'}).extract()
        article.find(True, {'class': 'abh_box'}).extract()
        article.find(True, {'class': 'sharedaddy'}).extract()
        article.find(True, {'class': 'post-foot'}).extract()
        article.find(True, id='nav-below').extract()


        # content = ''.join(map(str, all_content))
        mdcontent = html2md(str(article))
        htmlcontent = md2html(mdcontent)

        return {
            'title': title,
            'author': author,
            'headimg': None,
            'md': mdcontent,
            'html': htmlcontent,
        }

    @staticmethod
    def is_content(tag):
        if isinstance(tag, NavigableString):
            return True
        if tag.name in ('script', 'ins'):
            return False
        if tag.name == 'img' and tag.get('alt', None) == 'Fb-Button':
            return False
        klass = tag.get('class', ())
        if {'postitle', 'single-metainfo',
                'fcbk_share', 'abh_box', 'sharedaddy',
                'adsbygoogle', 'post-foot',
                'fcbk_button', 'fcbk_like'}.intersection(klass):
            return False
        if tag.get('id', None) == 'nav-below':
            return False
        return True

    @classmethod
    def fix_img(cls, imgsoup, source):
        src = imgsoup['src']
        imgurl = urlsplit(src)
        if not imgurl.netloc:
            sourceurl = urlsplit(source)
            newsrc = list(imgurl)
            newsrc[0] = sourceurl.scheme
            newsrc[1] = sourceurl.netloc

            imgtag = imgsoup.new_tag("img")
            imgtag['src'] = urlunsplit(newsrc)
            alt = imgsoup.get('alt', None)
            if alt is not None:
                imgtag['alt'] = alt
            title = imgsoup.get('title', None)
            if title is not None:
                imgtag['title'] = title

            imgsoup.replace_with(imgtag)


if __name__ == '__main__':
    url = 'http://www.jollatides.com/2014/12/08/jolla-tablet-campaign-last-chance-to-order-juicy-perks/'
    host = LoadHandler.host(url)
    with open('/tmp/source.html', 'r', encoding='utf-8') as f:
        parsed = LoadHandler.parse_jollatides(BeautifulSoup(f.read()))
    print(parsed)
