import os
import tempfile
import logging
import jieba
from jieba.analyse.analyzer import ChineseAnalyzer
import whoosh.highlight
from whoosh.highlight import FIRST
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser
from lib.db.jolla import Article
from .base import BaseHandler

jieba.initialize()


class MookHightlighter(whoosh.highlight.Highlighter):
    def __init__(self, fragmenter=None, scorer=None, formatter=None,
                 always_retokenize=False, order=FIRST):
        formatter = formatter or whoosh.highlight.HtmlFormatter(tagname='mark')
        super(MookHightlighter, self).__init__(fragmenter, scorer, formatter,
                                               always_retokenize, order)


whoosh.highlight.Highlighter = MookHightlighter


# TODO: cache
class SearchHandler(BaseHandler):
    logger = logging.getLogger('jolla.search')
    analyzer = ChineseAnalyzer()
    tmp_dir = os.path.join(tempfile.gettempdir(), 'jolla_search')

    def get(self, search=None):
        query = self.get_search(search)
        if query is None:
            return

        self.build_search()
        self.debug('search for %s', query)
        result = self.search(query)
        return self.render(
            'jolla/search.html',
            key=query,
            result=self.to_article_instance(result),
        )

    def get_search(self, search):
        if search is None:
            search = self.get_argument('search')
            if ' ' in search:
                search = search.replace(' ',  '+')

            self.redirect('/search/%s/' % search)
            return

        if ' ' in search:
            self.redirect(self.request.uri.replace(' ', '+'))
            return

        return search.replace('+', ' ')

    @classmethod
    def build_search(cls):
        analyzer = cls.analyzer

        schema = Schema(
            nid=ID(unique=True, stored=True),
            slug=ID(unique=True, stored=True),
            title=TEXT(stored=True, analyzer=analyzer),
            tag=KEYWORD(stored=True, lowercase=True, commas=True,
                        scorable=True),
            description=TEXT(stored=True, analyzer=analyzer),
            content=TEXT(stored=True, analyzer=analyzer)
        )

        folder = cls.tmp_dir
        if not os.path.exists(folder):
            os.mkdir(folder)
        create_in(folder, schema)

        ix = open_dir(folder)
        writer = ix.writer()

        for article in Article.find({'status': Article.ACCEPTED}):
            writer.update_document(
                nid=str(article._id),
                slug=article.slug,
                title=article.title,
                tag=','.join(article.tag),
                description=article.description,
                content=article.content
            )

        writer.commit()

        cls.searcher = ix.searcher()

    def search(self, word):
        searcher = self.searcher
        with searcher as searcher:
            query = MultifieldParser(
                ['title', 'tag', 'description', 'content'],
                searcher.schema).parse(word)

            results = searcher.search(query, limit=None)
            for each in results:
                yield each

    def to_article_instance(self, results):
        for each in results:
            article = Article()
            result = each.fields()
            result['tag'] = result['tag'].split(',')
            article.update(result)
            article.highlights = each.highlights
            yield article
