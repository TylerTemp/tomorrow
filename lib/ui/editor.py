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

    def embedded_css(self):
        return '''#markdownEditor {
                resize:vertical;
                overflow:auto;
                min-height:100px;
                padding:1em;
            }'''

    def javascript_files(self):
        return ('/static/js/md/html2md.min.js',
                '/static/js/md/md2html.min.js',
                '/static/js/md/editor-wysiwyg.js')


class MdEditorModule(tornado.web.UIModule):
    pass
