import logging
import json

import sys
import os
sys.path.insert(0, os.path.normpath(
                    os.path.join(__file__, '..', '..', '..', '..')))
from lib.hdlr.base import BaseHandler, EnsureUser
from lib.db import Wordz
sys.path.pop(0)

logger = logging.getLogger('tomorrow.project.wordz.home')

class QuizHandler(BaseHandler):

    @EnsureUser(active=True)
    def get(self):
        tag = self.get_argument('tag', None)
        if tag:
            return self.get_tag(tag)
        else:
            return self.render_page()

    def get_tag(self, tag):
        collect = []
        for each in Wordz.find_tag(tag):
            each['id'] = str(each.pop('_id'))
            collect.append(each)

        self.write(json.dumps(collect))

    def render_page(self):
        user_info = self.current_user
        username = user_info['user']
        tags = self.get_user_tags(username)
        return self.render(
            'project/wordz/quiz.html',
            tags=tags
        )

    def get_user_tags(self, username):
        all_words = Wordz.find_by_user(username)
        tags = set()
        for each in all_words:
            for tag in each['tag']:
                if tag not in tags:
                    tags.add(tag)
                    yield tag