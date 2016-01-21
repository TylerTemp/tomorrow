import tornado.web
import logging

from lib.config.tomorrow import Config

logger = logging.getLogger('tomorrow.ui.editor')
config = Config()

class ErrorImageModule(tornado.web.UIModule):

    def render(self, code):
        host = config.tomorrow_host
        return (
            '<div class="am-cf">'
            '<img src="//{host}/utility/woopse/{code}/" '
            'class="swing am-img-responsive am-center am-padding">'
            '</div>'
        ).format(host=host, code=code)

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
