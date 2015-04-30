# tomorrow

website code for [tomorrow.becomes.today](http://tomorrow.becomes.today)

Note it's developing and hasn't finished.

# Install

Require python >= 3.3

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

you can run 4 processes on port 8001~8004(can't change) by

```bash
python3 lib/tool/reboot.py
```

this can also help you reboot the server.

you can also shutdown the server by

```bash
python3 lib/tool/shutdown.py
```

# Configuration

run the following command will generate a `config.conf` file in main folder

```bash
python lib/config.py
```

this `config.conf` is in json format. Read the comment for details

Note you can shadow those settings by pass args to `main.py` or `lib/tool/reboot.py` in command line

## reference
* UI by [amazeUI](http://amazeui.org/)
* `lib/tracemore.py` from &#60;Python Cockbook&#62;
* `lib/bashlog.py` from `tornado.logging`
* `static/js/html2md.js` from [github: neocotic/html.md](https://github.com/neocotic/html.md)
* `static/js/md2html.js` is under MIT license, by Dominic Baggott, Ash Berlin & Christoph Dorn <christoph@christophdorn.com> (http://www.christophdorn.com)
* jquery-textrange from [github:dwieeb/jquery-textrange](https://github.com/dwieeb/jquery-textrange)
* `static/js/jquery/jquery.cookie.js` from [github:carhartl/jquery-cookie](https://github.com/carhartl/jquery-cookie)
* `lib/tool/filelock.py` edit from [github: dmfrey/ FileLock](https://github.com/dmfrey/FileLock)
