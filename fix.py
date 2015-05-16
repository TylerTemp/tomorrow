from lib.db import Jolla, Article

j = Jolla('Welcome-to-the-official-Jolla-Blog!')
a = Article('Welcome-to-the-official-Jolla-Blog!')
assert not j.new
assert not a.new

j.get()['headimg'] = 'https://dn-jolla.qbox.me/welcome_image.jpeg'
a.get()['transinfo']['headimg'] = 'https://dn-jolla.qbox.me/welcome_image.jpeg'

j.save()
a.save()
