import tornado.web
import logging
import time
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

logger = logging.getLogger('tomorrow.ui.html')


class TimeModule(tornado.web.UIModule):

    def render(self, t, fmt='%Y-%m-%d'):
        fmt = '<time datetime="%s">%s<time>'
        t = time.localtime(t)
        attr = time.strftime('%Y-%m-%dT%H:%M:%S', t)
        display_time = time.strftime('%Y-%m-%d', t)
        return fmt % (attr, display_time)


class TagModule(tornado.web.UIModule):

    def render(self, tags):
        result = []
        for num, (tag1, tag2) in enumerate(zip_longest(tags[::2], tags[1::2])):
            if num > 3:
                result.append('...')
                break
            first = ('<span class="am-badge am-badge-success am-radius">'
                     '%s'
                     '</span>') % self.locale.translate(tag1)
            result.append(first)

            if tag2 is None:
                break
            else:
                second = ('<span class="am-badge am-badge-primary am-radius">'
                          '%s'
                          '</span>') % self.locale.translate(tag2)
            result.append(second)

        return ' '.join(result)