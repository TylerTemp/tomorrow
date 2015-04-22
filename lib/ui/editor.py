import tornado.web
import logging

logger = logging.getLogger('ui.editor')


class MdWysiwygEditorModule(tornado.web.UIModule):

    def render(self, switch=False, upload_img=None, upload_file=None, content=''):
        return self.render_string(
            'uimodule/editor-wysiwyg.html',
            upload_img=upload_img,
            upload_file=upload_file,
            switch=switch,
            content=content,
        )


class MdEditorModule(tornado.web.UIModule):

    def render(self, switch=False, upload_img=None, upload_file=None, content=''):
        return self.render_string(
            'uimodule/editor-md.html',
            upload_img=upload_img,
            upload_file=upload_file,
            switch=switch,
            content=content,
        )
