import tornado.web
import logging

logger = logging.getLogger('ui.editor')


class MdWysiwygEditorModule(tornado.web.UIModule):

    def render(self, switch=False, content=''):
        return self.render_string(
            'uimodule/editor-wysiwyg.html',
            switch=switch,
            content=content,
        )

class MdEditorModule(tornado.web.UIModule):

    def render(self, switch=False, content=''):
        return self.render_string(
            'uimodule/editor-md.html',
            switch=switch,
            content=content,
        )
