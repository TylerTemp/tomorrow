# tomorrow

website code for [tomorrow.comes.today](http://tomorrow.comes.today) and [jolla.comes.today](http://jolla.comes.today)

Note it's developing and hasn't finished yet.

# Install

Require python >= 3.3 & MongoDB

It may or may not run on python2.7 (not test)

```bash
git clone https://github.com/TylerTemp/tomorrow.git
cd tomorrow
pip3 install -r requirement.txt
```

# Run

run in single process:

```bash
cd path/to/tomorrow
python3 main.py -p 8000
```

# Configuration & multiprocess

all default configurations are under source code of
`lib/config/`, please read the source code of that part to change the
configuration by creating a `.conf` file

To run multi-processes:

```bash
python3 lib/tool/reboot.py
```

Note you can shadow those settings by passing args to `main.py` or `lib/tool/reboot.py` in command line

`reboot.py` accept the same command line args except `-p`,
use `python main.py --help` for more detail

## clean code ##

```
python -c 'from lib.db.tomorrow import Auth; Auth.clean_codes_and_tokens()'
```

## Project & Service

`tomorrow` uses the following projects & services. Much thanks to these awesome work!

*   [python3](http://python.org) - A programming language that lets you work quickly and integrate systems more effectively
*   [python-tornado](http://www.tornadoweb.org/en/stable/) - A Python web framework and asynchronous networking library
*   [python-docpie](https://github.com/TylerTemp/docpie.git) - An easy and Pythonic way to create your POSIX command line
*   [MongoDB](https://www.mongodb.org/) & [python-pymongo](https://api.mongodb.org/python/current/) - A powerful NoSQL database and its python interact implement
*   [python-passlib](https://bitbucket.org/ecollins/passlib) - A python encrypt/decrypt module
*   [python-bleach](https://github.com/jsocol/bleach) - an HTML sanitizing library that escapes or strips markup and attributes based on a white list
*   [python-html2text](https://github.com/aaronsw/html2text) - A Python script that converts a page of HTML into clean, easy-to-read plain ASCII text(MarkDown format)
*   [python-markdown](https://pythonhosted.org/Markdown/) - A Python implementation of John Gruber’s Markdown
*   [python-markdown-nlcontinuous](https://github.com/TylerTemp/md-nlcontinuous.git) - Python Markdown extension which prevents white space after line break in Chinese
*   [python-markdown-amazedown](https://github.com/TylerTemp/amazedown.git) - Python-Markdown plug-in to support Amaze-UI style HTML UI Framework
*   [python-markdown-video](https://github.com/TylerTemp/md-video) - video block(tag) extension for Python-Markdown
*   [python-markdown-underline](https://github.com/TylerTemp/md-underline) - underline plugin for python markdown
*   [python-BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/bs4/) - A Python library designed for quick turnaround projects like screen-scraping
*   [weibo](https://pypi.python.org/pypi/weibo/0.2.2) - Sina Weibo API for python
*   [amazeUI](http://amazeui.org/) - A Chinese friendly lightweight mobile first web frame
*   [QiNiu](http://qiniu.com) - A fast, free and powerful CDN service
*   [iconfont](http://www.iconfont.cn) - A web icon font maker
*   [github:dwieeb/jquery-textrange](https://github.com/dwieeb/jquery-textrange) - a JS tool that can select text in `input` and `textarea` conveniently
*   `lib/tracemore.py` from [*Python Cockbook*](http://www.amazon.com/Python-Cookbook-Third-David-Beazley/dp/1449340377/ref=sr_1_1?ie=UTF8&qid=1430528366&sr=8-1&keywords=python+cookbook)
*   `lib/bashlog.py` from `tornado.logging`
*   `static/js/html2md.js` from [github: neocotic/html.md](https://github.com/neocotic/html.md)
*   [github: showdown](https://github.com/showdownjs/showdown) -  A Javascript
    lib that can convert markdown (html allowed) to html
*   `static/js/md2html.js` is under MIT license, by Dominic Baggott, Ash Berlin & Christoph Dorn <christoph@christophdorn.com> (http://www.christophdorn.com)
*   `lib/tool/filelock.py` is edited from source [github: dmfrey/ FileLock](https://github.com/dmfrey/FileLock)
*   [highlight.js](https://highlightjs.org/) - Syntax highlighting for the Web
*   [medialize-URI.js](https://github.com/medialize/URI.js) - JavaScript URL mutation library

Note for the file `static/img/user.jpg`, I can not find the source, nor do I know the license. If you know the source/license, or it has infringed your right, please tell me at <tylertempdev@gmail.com>.
