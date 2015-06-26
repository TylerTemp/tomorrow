# tomorrow

website code for [tomorrow.becomes.today](http://tomorrow.becomes.today)

Note it's developing and hasn't finished.

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

run the following command to generate a `config.conf` file in the main folder

```bash
python lib/config.py
```

(this `config.conf` is in json format. Read the comment for details)

open `config.conf`, change `"ports": [8001, 8002, 8003, 8004]` to
any ports you want to run

then run multiprocess by

```bash
python3 lib/tool/reboot.py
```

Note you can shadow those settings by passing args to `main.py` or `lib/tool/reboot.py` in command line

`reboot.py` accept the same command line args except `-p`,
use `python main.py --help` for more detail

## reference

* UI powered by [amazeUI](http://amazeui.org/)
* CDN powered by [QiNiu](http://qiniu.com)
* Comment powered by [DuoShuo](http://duoshuo.com)
* `lib/tracemore.py` from [*Python Cockbook*](http://www.amazon.com/Python-Cookbook-Third-David-Beazley/dp/1449340377/ref=sr_1_1?ie=UTF8&qid=1430528366&sr=8-1&keywords=python+cookbook)
* `lib/bashlog.py` from `tornado.logging`
* `static/js/html2md.js` from [github: neocotic/html.md](https://github.com/neocotic/html.md)
* `static/js/md2html.js` is under MIT license, by Dominic Baggott, Ash Berlin & Christoph Dorn <christoph@christophdorn.com> (http://www.christophdorn.com)
* jquery-textrange from [github:dwieeb/jquery-textrange](https://github.com/dwieeb/jquery-textrange)
* `lib/tool/filelock.py` is edited from source [github: dmfrey/ FileLock](https://github.com/dmfrey/FileLock)

Note for the file `static/img/user.jpg`, I can not find the source, nor do I know the license. If you know the source/license, or it has infringed your right, please tell me at <tylertempdev@gmail.com>.
