import tornado.web
import logging


logger = logging.getLogger('tomorrow.ui.author')


class AuthorModule(tornado.web.UIModule):

    def render(self, name):
        info = self.get_info(name)
        if not info:
            return ''
        return self.render_string(
            'uimodule/author.html',
            name=name,
            content=info[0],
            img=info[1],
        )

    def get_info(self, name):
        if name == 'JuhaniLassila':
            content = '''
            Jolla通讯部主管。
            国际公关和通讯专家。
            音乐爱好者。
            Jolla巡演队（以及其它乐队）吉他手。'''
            img = 'https://dn-jolla.qbox.me/Jussi1-150x150.jpg'
            return (content, img)
        if name == 'Stefano Mosconi':
            content = '''
            Jolla联合创始人，首席技术官。
            一个拥有社交技巧和商业头脑的极客。
            An entrepreneur with a touch for people and for fixing stuff.
            喜爱食物、小玩意、摄影和骑行，顾家。'''
            img = 'https://dn-jolla.qbox.me/Stefano Mosconi.jpg'
            return (content, img)
        return None
