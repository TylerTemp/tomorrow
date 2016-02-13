from bson import ObjectId
from bson.errors import InvalidId
import logging
import tornado.web
from ..base import BaseHandler, EnsureUser
from lib.db.jolla import User
from lib.tool.b64 import decode_data_url

class UserHandler(BaseHandler):
    logger = logging.getLogger('jolla.manage.user')

    @EnsureUser(EnsureUser.ROOT)
    def get(self):

        return self.render(
            'jolla/manage/user.html',
            users=self.all_users(),
        )

    def all_users(self):
        for each in User.all():
            u = User()
            u.update(each)
            yield u

    @EnsureUser(EnsureUser.ROOT)
    def post(self):
        if self.get_argument('action', None) == 'delete':
            return self.delete_user()

        return self.modify_user()

    def delete_user(self):
        u = self.get_user()
        u.remove()

        return self.write({'error': 0})

    def get_user(self):
        uid = self.get_argument('_id')
        try:
            _id = ObjectId(uid)
        except InvalidId:
            raise tornado.web.HTTPError(400, 'Invalid Id %r' % uid)

        u = User(ObjectId(uid))
        if not u:
            raise tornado.web.HTTPError(404, 'User %r not found' % uid)

        return u


    def modify_user(self):
        user = self.get_user()
        user.type = self.get_user_type()
        user.photo = self.get_avatar(user._id)
        user.name = self.get_argument('name', '').strip() or None
        user.email = self.get_argument('email', '').strip() or None
        user.home = self.get_argument('home', '').strip() or None

        zh = user.zh
        zh['intro'] = self.get_argument('zh-intro', '').rstrip() or None
        zh['donate'] = self.get_argument('zh-donate', '').rstrip() or None

        en = user.en
        en['intro'] = self.get_argument('en-intro', '').rstrip() or None
        en['donate'] = self.get_argument('en-donate', '').rstrip() or None

        user.save()

        self.write({
            'error': 0,
            'name': user.name,
            'email': user.email,
            'photo': user.photo,
            'type': user.type,
            'zh_intro': user.zh.get('intro', None),
            'zh_donate': user.zh.get('donate', None),
            'en_intro': user.en.get('intro', None),
            'en_donate': user.en.get('donate', None),
        })

    def get_user_type(self):
        t = self.get_argument('group')
        invalid = False
        try:
            t = int(t)
        except ValueError:
            invalid = True

        if not invalid and t not in (User.DEACTIVE, User.NORMAL, 
                                     User.ADMIN, User.ROOT):
            invalid = True

        if invalid:
            raise tornado.web.HTTPError(400, 'Invalid group %r' % t)

        return t

    def get_avatar(self, _id):
        direct = self.get_argument('avatar', None)
        if direct is not None:
            return direct

        files = self.request.files
        if 'avatar' not in files:
            return None

        f = files['avatar'][0]
        content = f['body']
        name = f['filename']
        fname = str(_id)
        ext = os.path.splitext(name)[-1]
        if ext:
            fname += ext

        return self.save_avatar(decode_data_url(content), fname)


    def save_avatar(self, content, fname):

        fpath = os.path.join(self.config.root, 'static', 'avatar', fname)
        self.info('save to %s', fpath)
        with open(fpath, 'wb') as f:
            f.write(content)

        return '/static/avatar/%s' % name
