from lib.hdlr.base import BaseHandler

class TakeOutCalculateHandler(BaseHandler):

    def get(self):
        return self.render(
            'utility/take-out-calculate.html'
        )