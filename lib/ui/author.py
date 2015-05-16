# coding: utf-8
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
            喜爱食物、小玩意、摄影和骑行，顾家的好男人。'''
            img = 'https://dn-jolla.qbox.me/Stefano Mosconi.jpg'
            return (content, img)
        if name == 'Marc Dillon':
            content = '''
            Jolla创始人，首席运营官。
            手机技术的全球发言人和思想领导。
            吉他手，歌手，摩托车骑手，狂热的机械和电子爱好者。
            '''
            img = 'https://dn-jolla.qbox.me/Marc_Dillon.jpg'
            return (content, img)
        if name == 'Soumya Bijjal':
            content = '''
            Jolla项目经理。
            Linux狂热爱好者。
            '''
            img = 'https://dn-jolla.qbox.me/Soumya Bijjal.jpeg'
            return (content, img)
        if name == 'Juha Paakkari':
            # what does "Passionate about things that really matter and
            # about keeping them moving." mean?
            return (
                '''Jolla营销主管。
                对重要的事情充满热情。
                ''',
                'https://dn-jolla.qbox.me/Juha Paakkari.jpeg'
            )
        if name == 'Carsten Munk':
            return (
                '''
                Jolla首席研究工程师。
                经常从一些奇奇怪怪的东西中获得Sailfish系统新特性和革新的灵感。
                热衷于开源透明的开发。
                ''',
                'https://dn-jolla.qbox.me/Carsten Munk.png'
            )
        if name == 'Antti Saarnio':
            return (
                '''Jolla联合创始人，董事会主席。
                大无畏的企业家和商业冒险家。
                ''',
                'https://dn-jolla.qbox.me/Antti Saarnio.png'
            )
        if name = 'Carol Chen':
            return (
                '''Jolla社区主管。
                全球（星级）星舰迷。
                热爱开源和开放的社区。
                会用鼓、琴和嗓音创造不错的音乐。
                ''',
                'https://dn-jolla.qbox.me/Carol-Chen.jpeg'
            )
        if name == 'Marko Saukko':
            return (
                '''
                自2012年2月起任Jolla手机工程师。
                Nemo手机工程维护者，Mer项目维护者，拥有数年硬件自适应工作经验。
                摄影和电子游戏狂热爱好者。
                ''',
                'https://dn-jolla.qbox.me/Marko Saukko.jpg'
            )
        if name == 'Pauliina Alanen':
            return (
                '''
                Jolla通讯和营销助理。
                热衷于各种媒体。
                爱好唱歌和弹钢琴。
                ''',
                'https://dn-jolla.qbox.me/Pauliina Alanen.jpg'
            )
        if name == 'Martin Schüle':
            return (
                '''
                Jolla首席执行师。
                醉心于宏观和交叉学科设计。
                顾家，喜欢翻修老木房，也喜欢手球。
                ''',
                'https://dn-jolla.qbox.me/Martin Schüle.jpg'
            )
        return None
