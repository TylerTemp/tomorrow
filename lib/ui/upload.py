import tornado.web
import logging


class UploadFileModule(tornado.web.UIModule):

    def render(self):
        return self.render_string(
            'uimodule/uploadfile.html'
        )


class UploadImageModule(tornado.web.UIModule):

    def render(self):
        return self.render_string(
            'uimodule/uploadimage.html'
        )
