import logging
import os
import base64
try:
    from io import BytesIO
except ImportError:
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO
import tornado.web
import cairocffi as cairo

from lib.config.tomorrow import Config
from lib.tool import b64
# from lib.hdlr.utility.whoops import WoopseHandler

logger = logging.getLogger('tomorrow.ui.editor')
config = Config()

class ErrorImageModule(tornado.web.UIModule):

    base = os.path.normpath(
            os.path.join(__file__, '..', '..', '..',
                         'static', 'img', 'error'))
    with open(os.path.join(base, 'puzzle.png'), 'rb') as f:
        puzzle_png = BytesIO(f.read())

    def render(self, code):
        # host = config.tomorrow_host
        img = self.mk_img(str(code))
        # b64_string = base64.b64encode(img).decode('utf-8')
        # data_url = 'data:image/gif;base64,' + b64_string
        data_url = b64.gen_data_url(img, is_byte=True)
        return (
            '<div class="am-cf">'
            '<img src="{src}" '
            'class="swing am-img-responsive am-center am-padding">'
            '</div>'
        ).format(src=data_url)

    def _cache(func):
        _cache_result = {}

        def wrapper(self, nums):
            if nums not in _cache_result:
                result = func(self, nums)
                _cache_result[nums] = result

            return _cache_result[nums]

        return wrapper

    @_cache
    def mk_img(self, nums):
        source_png = self.puzzle_png
        source_png.seek(0)
        source = cairo.ImageSurface.create_from_png(source_png)
        bg_context = cairo.Context(source)

        num_surface = cairo.ImageSurface.create_from_png(
                BytesIO(self.get_num_data(nums)))

        x, y = self.find_position(num_surface.get_width(),
                                  num_surface.get_height(),
                                  source.get_width(),
                                  source.get_height())

        bg_context.set_source_surface(num_surface, x, y)
        bg_context.paint()

        result = BytesIO()
        source.write_to_png(result)
        return result.getvalue()

    def find_position(self, s_width, s_height, b_width, b_height):
        left = (b_width - s_width) / 2.0
        top = (b_height - s_height) / 2.0
        return (left, top)

    def get_num_file(self, num):
        with open(os.path.join(self.base, '%s.png' % num), 'rb') as f:
            return BytesIO(f.read())

    def get_num_data(self, nums):
        surfaces = []
        for each in nums:
            surfaces.append(
                    cairo.ImageSurface.create_from_png(
                            self.get_num_file(each)))
        width = 0
        height = 0
        gap = 10
        for each in surfaces:
            this_width = each.get_width()
            this_height = each.get_height()
            width += (this_width + gap)
            height = max(height, this_height)
        else:
            width -= gap

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        surface_context = cairo.Context(surface)
        surface_context.set_source_rgba(0, 0, 0, 1)
        currect_x = 0
        for each_surface in surfaces:
            surface_context.set_source_surface(each_surface, currect_x)
            surface_context.paint()
            currect_x += (each_surface.get_width() + gap)
        surface_context.paint()

        result = BytesIO()
        surface.write_to_png(result)
        return result.getvalue()

    def embedded_css(self):
        return '''
        .swing {
            -moz-animation: 3s ease 0s normal none infinite swing;
            -moz-transform-origin: center top;
            -webkit-animation:swing 3s infinite ease-in-out;
            -webkit-transform-origin:top;
            max-width: 500px;
        }

        @-moz-keyframes swing{
            0%{-moz-transform:rotate(-7deg)}
            50%{-moz-transform:rotate(7deg)}
            100%{-moz-transform:rotate(-7deg)}
        }

        @-webkit-keyframes swing{
            0%{-webkit-transform:rotate(-7deg)}
            50%{-webkit-transform:rotate(7deg)}
            100%{-webkit-transform:rotate(-7deg)}
        }'''
