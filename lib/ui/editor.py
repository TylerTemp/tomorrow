import tornado.web
import logging

logger = logging.getLogger('ui.editor')


class EditorModule(tornado.web.UIModule):
    pass


class MdWysiwygEditorModule(tornado.web.UIModule):

    def render(self, content=''):
        return self.render_string(
            'uimodule/editor-wysiwyg.html',
            content=content,
        )

class MdEditorModule(tornado.web.UIModule):

    def render(self, content=''):
        return self.render_string(
            'uimodule/editor-md.html',
            content=content,
        )
