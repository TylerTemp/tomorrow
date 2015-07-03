# coding: utf-8
# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote, quote

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import JollaAuthor
sys.path.pop(0)

JollaAuthor._jolla_author.drop()

info = (
    {
        'name': 'JuhaniLassila',
        'photo': 'https://dn-jolla.qbox.me/Jussi1-150x150.jpg',
        'description': 'Head of Communications for Jolla. International PR &amp; Communications professional. Music enthusiast. Guitarist in the Jolla Cruise Band, among other bands.',
        'translation': '''
Jolla通讯部主管。
国际公关和通讯专家。
音乐爱好者。
Jolla巡演队（以及其它乐队）吉他手。'''
    },
    {
        'name': 'Stefano Mosconi',
        'photo': 'https://dn-jolla.qbox.me/Stefano Mosconi.jpg',
        'description': 'CTO and Co-founder of Jolla. A geek with social skills and business acumen. An entrepreneur with a touch for people and for fixing stuff. Loves food, gadgets, photography, family, cycling.',
        'translation': '''
Jolla联合创始人，首席技术官。
一个拥有社交技巧和商业头脑的极客。
一个善于交际又喜欢修理物件的企业家。
爱食物，爱小玩意，爱摄影，爱家人，爱骑行。'''
    },
    {
        'name': 'Marc Dillon',
        'photo': 'https://dn-jolla.qbox.me/Marc_Dillon.jpg',
        'description': 'COO and Co-founder of Jolla. Global speaker and thought leader in mobile technology. Guitarist & singer, motorcyclist, and enthusiastic in mechanics & electronics.',
        'translation': '''
Jolla创始人，首席运营官。
手机技术的全球发言人和思想领导。
吉他手，歌手，摩托车骑手，狂热的机械和电子爱好者。
'''
    },
    {
        'name': 'Soumya Bijjal',
        'photo': 'https://dn-jolla.qbox.me/Soumya Bijjal.jpeg',
        'description': 'Software Program Manager at Jolla. A Linux enthusiast in search of a TARDIS.',
        'translation': '''Jolla项目经理。
Linux狂热爱好者。'''
    },
    {
        'name': 'Juha Paakkari',
        'photo': 'https://dn-jolla.qbox.me/Juha Paakkari.jpeg',
        'description': 'Head of Go-To-Market at Jolla. Passionate about things that really matter and about keeping them moving.',
        'translation': None
    },
    {
        'name': 'Carsten Munk',
        'photo': 'https://dn-jolla.qbox.me/Carsten Munk.png',
        'description': 'Chief Research Engineer at Jolla. Works with all sorts of strange things to bring you future SailfishOS devices and innovation for them. Passionate about open source and transparency in development.',
        'translation': '''
Jolla首席研究工程师。
经常从一些奇奇怪怪的东西中获得Sailfish系统新特性和革新的灵感。
热衷于开源透明的开发。
'''
    },
    {
        'name': 'Antti Saarnio',
        'photo': 'https://dn-jolla.qbox.me/Antti Saarnio.png',
        'description': 'Co-founder and Chairman of the Board of Jolla. Fearless entrepreneur and business adventurer.',
        'translation': '''Jolla联合创始人，董事会主席。
大无畏的企业家和商业冒险家。'''
    },
    {
        'name': 'Carol Chen',
        'photo': 'https://dn-jolla.qbox.me/Carol-Chen.jpeg',
        'description': 'Community Chief at Jolla. Globe (and star) trekker. Ardent about open source and open communication. Makes decent music with timpani, drums, piano, and vocal cords.',
        'translation': '''Jolla社区主管。
全球（星级）星舰迷。
热爱开源和开放的社区。
会用定音鼓、架子鼓和钢琴配着嗓音创作出不错的音乐。
'''
    },
    {
        'name': 'Marko Saukko',
        'photo': 'https://dn-jolla.qbox.me/Marko Saukko.jpg',
        'description': 'Chief Engineer at Jolla since Feb 2012. Maintainer of the Nemo Mobile project, also involved with the Mer Project, with years of experience on hardware adaptation work. Photography and video game enthusiast.',
        'translation': '''自2012年2月起任Jolla手机工程师。
Nemo手机工程维护者，Mer项目维护者，拥有数年硬件自适应工作经验。
摄影和电子游戏狂热爱好者。'''
    },
    {
        'name': 'Pauliina Alanen',
        'photo': 'https://dn-jolla.qbox.me/Pauliina Alanen.jpg',
        'description': 'Communications and Marketing Assistant for Jolla. Passionate about media in all its diversity. Loves singing and playing the piano.',
        'translation': '''Jolla通讯和营销助理。
热衷于各种媒体。
爱好唱歌和弹钢琴。'''
    },
    {
        'name': 'Martin Schüle',
        'photo': 'https://dn-jolla.qbox.me/Martin Schüle.jpg',
        'description': 'Chief Designer of Jolla. Passionate about holistic and multidisciplinary design. Loves his family, renovating old wooden houses, as well as playing handball.',
        'translation': '''Jolla首席执行师。
醉心于宏观和交叉学科设计。
顾家，喜欢翻修老木房，也喜欢手球。'''
    },
    {
        'name': 'Iekku Pylkkä',
        'photo': 'https://dn-jolla.qbox.me/Iekku Pylkkä.jpeg',
        'description': 'Head of Developer Affairs at Jolla. Interested in QA, open source, developer community and communication. Punk, nature, singing, badgers and Shetland sheepdogs are near to heart.',
        'translation': '''Jolla开发人员事务主管。
喜欢QA、开源、开发者社区和交流。
Punk, nature, singing, badgers and Shetland sheepdogs are near to heart。'''
    }
)

for each in info:
    print(each['name'])
    author = JollaAuthor(each['name'])
    author.photo = each['photo']
    author.description = each['description']
    author.translation = each['translation']
    author.save()
