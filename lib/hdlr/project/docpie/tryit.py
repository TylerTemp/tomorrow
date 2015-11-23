# coding: utf-8
import tornado.web
import logging
import time
import json
import shlex
import docpie
try:
    from io import StringIO
except ImportError:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

import sys
import os
sys.path.insert(0, os.path.normpath(
                    os.path.join(__file__, '..', '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.tool.tracemore import get_exc_plus
from lib.db import Article
sys.path.pop(0)

logger = logging.getLogger('tomorrow.project.docpie.try')
logging.getLogger('docpie').setLevel(logging.CRITICAL)

try:
    StrType = basestring
except NameError:
    StrType = str


class StdoutRedirect(StringIO):

    if sys.hexversion >= 0x03000000:
        def u(self, string):
            return string
    else:
        def u(self, string):
            return unicode(string)

    def write(self, s):
        super(StdoutRedirect, self).write(self.u(s))

    def __enter__(self):
        self.real_out = sys.stdout
        sys.stdout = self
        return super(StdoutRedirect, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.real_out
        return super(StdoutRedirect, self).__exit__(exc_type, exc_val, exc_tb)


class TryHandler(BaseHandler):

    _article_result = Article('docpie-example').get()
    _content = _article_result['en']['content']
    edit_time = _article_result['edittime']
    example = json.loads(_content)

    del _article_result
    del _content

    default = {'doc': None, 'argv': None, 'help': True, 'version': None,
               'stdopt': True, 'attachopt': True, 'attachvalue': True,
               'auto2dashes': True, 'name': None, 'case_sensitive': False,
               'optionsfirst': False, 'appearedonly': False}  #, 'extra': {}}

    t = docpie.__timestamp__

    def get(self):
        example = self.get_argument('example', None)
        result = dict(self.default)
        result['file_name'] = 'pie.py'
        output = None
        if example:
            target_example = self.get_example(example)
            result.update(target_example)
        else:
            doc = self.get_argument('doc', None)
            result['doc'] = doc or None
            if doc:
                argv = self.get_argument('argv')
                result['argv'] = argv
                name = self.get_argument('name', None) or None
                config = {
                    'help': self.get_bool('help'),
                    # may be empty str
                    'version': self.get_argument('version', None) or None,
                    'stdopt': self.get_bool('stdopt'),
                    'attachopt': self.get_bool('attachopt'),
                    'attachvalue': self.get_bool('attachvalue'),
                    'auto2dashes': self.get_bool('auto2dashes'),
                    'name': name,
                    'case_sensitive': self.get_bool('case_sensitive'),
                    'optionsfirst': self.get_bool('optionsfirst'),
                    'appearedonly': self.get_bool('appearedonly')
                }

                if name is not None:
                    result['file_name'] = name

                with StdoutRedirect() as stdout:
                    args = shlex.split('pie.py ' + argv)
                    try:
                        # \r\n can not be handled correctly so far
                        # It's a bug
                        pie = docpie.docpie(doc.replace('\r\n', '\n'), args,
                                            **config)
                    except BaseException as e:
                        # in pypy3, sys.exit() gives e.args[0] = None
                        output = e.args[0] or ''
                    else:
                        output = str(pie)

                    if not output.strip():
                        output = stdout.read()

                result.update(config)

        if self.is_ajax():
            return self.write(json.dumps({'output': output}))

        return self.render(
            'project/docpie/try.html',
            version=docpie.__version__,
            time=self.get_time(),
            doc=result.pop('doc'),
            argv=result.pop('argv'),
            file_name=result.pop('file_name'),
            output=output,
            modified=self.diff_config(result),
            config=result,
            jsonlize=json.dumps
        )

    def get_time(self):
        if self.locale.code.startswith('en'):
            return time.ctime(self.t)
        return time.strftime('%m月%d日，%H:%M', time.localtime(self.t))

    def diff_config(self, source):
        default = dict(self.default)
        default.pop('doc')
        default.pop('argv')
        result = {}
        for key, default_value in default.items():
            # logger.debug('%s = %s / %s', key, default_value, source[key])
            source_value = source[key]
            if default_value != source_value:
                if isinstance(source_value, StrType):
                    source_value = repr(source_value)
                result[key] = source_value

        return result

    def get_example(self, example):
        article = Article('docpie-example').get()
        edit_time = article['edittime']
        if edit_time > self.edit_time:    # refresh
            logger.debug('refresh docpie examples')
            # always save in class
            self.__class__.edit_time = edit_time
            self.__class__.example = json.loads(article['en']['content'])

        if example not in self.example:
            raise tornado.web.HTTPError(
                    404, '%s example not found' % example)

        return self.example[example]

