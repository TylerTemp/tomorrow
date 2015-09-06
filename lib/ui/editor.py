import tornado.web
import logging

logger = logging.getLogger('romorrow.ui.editor')


class WysBarModule(tornado.web.UIModule):

    def render(self, upload_img=None, upload_file=None):
        return self.render_string(
            'uimodule/wysbar.html',
            upload_img=upload_img,
            upload_file=upload_file,
        )


class MdBarModule(tornado.web.UIModule):

    def render(self, upload_img=None, upload_file=None):
        return self.render_string(
            'uimodule/mdbar.html',
            upload_img=upload_img,
            upload_file=upload_file,
        )
