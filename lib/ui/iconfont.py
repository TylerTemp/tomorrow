import tornado.web

class IconFontModule(tornado.web.UIModule):

    def render(self):
        return ''

    def embedded_css(self):
        return '''
@font-face {font-family: "iconfont";
  src: url('https://dn-tomorrow.qbox.me/iconfont.eot'); /* IE9*/
  src: url('https://dn-tomorrow.qbox.me/iconfont.eot?#iefix') format('embedded-opentype'), /* IE6-IE8 */
  url('https://dn-tomorrow.qbox.me/iconfont.woff') format('woff'), /* chrome、firefox */
  url('https://dn-tomorrow.qbox.me/iconfont.ttf') format('truetype'), /* chrome、firefox、opera、Safari, Android, iOS 4.2+*/
  url('https://dn-tomorrow.qbox.me/iconfont.svg#iconfont') format('svg'); /* iOS 4.1- */
}

.iconfont {
  font-family:"Segoe UI", "Lucida Grande", Helvetica, Arial, "Microsoft YaHei", FreeSans, Arimo, "Droid Sans","wenquanyi micro hei","Hiragino Sans GB", "Hiragino Sans GB W3", Arial, sans-serif, "iconfont";
  font-style:normal;
  -webkit-font-smoothing: antialiased;
  -webkit-text-stroke-width: 0.2px;
  -moz-osx-font-smoothing: grayscale;
}
.icon-md-simple:before { content: "\e604"; }
.icon-md-solid:before { content: "\e603"; }
.icon-jolla:before { content: "\e600"; }
'''
