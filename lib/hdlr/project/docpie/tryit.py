# coding: utf-8
import logging
import time
import json
import shlex
import docpie
try:
    from io import StringIO
except ImportError:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

import sys
import os
sys.path.insert(0, os.path.normpath(
                    os.path.join(__file__, '..', '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.tool.tracemore import get_exc_plus
sys.path.pop(0)

logger = logging.getLogger('tomorrow.project.docpie.try')
logging.getLogger('docpie').setLevel(logging.CRITICAL)

try:
    StrType = basestring
except NameError:
    StrType = str


class StdoutRedirect(StringIO):

    if sys.hexversion >= 0x03000000:
        def u(self, string):
            return string
    else:
        def u(self, string):
            return unicode(string)

    def write(self, s):
        super(StdoutRedirect, self).write(self.u(s))

    def __enter__(self):
        self.real_out = sys.stdout
        sys.stdout = self
        return super(StdoutRedirect, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.real_out
        return super(StdoutRedirect, self).__exit__(exc_type, exc_val, exc_tb)


class TryHandler(BaseHandler):

    example = {
        'ship':{
            'doc': """Naval Fate.

Usage:
  naval_fate ship new <name>...
  naval_fate ship <name> move <x> <y> [--speed=<kn>]
  naval_fate ship shoot <x> <y>
  naval_fate mine (set|remove) <x> <y> [--moored|--drifting]
  naval_fate -h | --help
  naval_fate -v | --version

Options:
  -h -? --help     Show this screen.
  -v --version     Show version.
  --speed=<kn>     Speed in knots. [default: 10]
  --moored         Moored (anchored) mine.
  --drifting       Drifting mine.""",
            'argv': 'ship Guardian move 10 50 --speed=20',
            'version': 'Naval Fate 2.0',
            'file_name': 'naval_fate'
        },

        'empty': {
            'doc': 'Usage: my_program\n\n\nThis program accepts no argument.',
        },


        'usage_elements': {
            'doc': '''\
Usage:
    pie.py [options] command <argument> --option
    pie.py [options] [optional-command] (REQUIRED-ARGUMENT)
    pie.py [options] (--either-this | --or-that)
    pie.py [options] <repeatable-arg>...


Example:
    pie.py command with --option
    pie.py is so cool''',
            'argv': 'argument',
        },

        'usage_argument': {
            'doc': '''\
Usage: pie.py <input> <output>
       pie.py INPUT OUTPUT

Example:
    pie.py /tmp/in.txt /tmp/out.txt''',
        },

        'get_help_pull': {
            'doc': '''\
Usage: get help pull


This program only accepts `help pull`''',
            'argv': 'help pull',
        },

        'optional_all_element': {
            'doc': '''\
Usage: pie.py [command --option ARGUMENT]


This is equal to `[command] [--option] [ARGUMENT]`''',
            'argv': 'command --option all',
        },

        'optional_required_either': {
            'doc': '''\
Usage: my_program [(command --option ARGUMENT)]

These 3 elements must all appear or be omitted.''',
            'argv': 'command --option arg',
        },

        'optional_respective_element': {
            'doc': 'Usage: pie.py [command] [--option] [<argument>]',
        },
        'required_either': {
            'doc': '''
Usage: pie.py (--this [<arg>] | --that)


Example:
    pie.py --this
    pie.py --this element
    pie.py --that''',
        },

        'exclusive_good': {
            'doc': '''\
Usage: pie.py (-vvv | -vv | -v)

Example:
    pie.py -v -vv
    pie.py -v -v
    pie.py -v'''
        },

        'exclusive_bad': {
            'doc': '''\
Usage: pie.py [-v | -vv | -vvv]''',
            'argv': '-v -v'
        },

        'exclusive_rank': {
            'doc': '''\
Usage: pie.py (--first | --second | --third)

Example:
    pie.py --first
    pie.py --second
    pie.py --third
'''
        },
        'cp': {
            'doc': 'Usage: cp <source>... <target> <logfile>',
            'argv': 'a.txt b.txt c.txt ~/Documents/ -'
        },

        'ellipsis_option': {
            'doc': '''
Usage: pie.py -a<arg>...
       pie.py --all=<arg>...

Example:
    pie.py -a 1 2 3
    pid.py --all 1 2 3''',
            'argv': '-a 1 2 3 4 5'
        },
        'ellipsis_option_unit': {
            'doc': '''\
Usage: pie.py (-a<arg>)...
       pie.py (--all=<arg>)...

Example:
    pie.py -a 1 -a 2  -a 3
    pie.py --all=1 --all=2 --all=3''',
            'argv': '--all=1 --all 2 --all=3'
        },
        'terminate_option': {
            'doc': '''\
Usage:
  program [options] now

Options:
  --terminate  terminate the daemon process
  --reload     reload the config file
  --restart    restart the service''',
            'argv': '--reload --restart now'
        },

        'terminate_oneline': {
            'doc': 'Usage: program [--terminate] [--reload] [--restart] now',
            'argv': '--terminate now'
        },

        'double_dashes_cat': {
            'doc': 'Usage: pie.py [-b] [-e] [<file>...]',
            'argv': '-- -v --help.txt'
        },
        'myscript.py': {
            'doc': '''\
Usage:
    myscript.py config
    $ python myscript.py make
    $ sudo python myscript.py make install''',
            'argv': 'make install',
            'name': 'myscript.py'
        },
        'helloworld': {
            'doc': 'Usage: prog <hello>',
            'argv': '-- --world'
        },
        'opt71': {
            'doc': '''\
Usage:
    pie.py [-f LEVEL] [--] <items>...

Test for docopt issue #71 in docpie
when `auto2dashes` is off, `-f -- 1 2 ` should fail.''',
            'auto2dashes': False,
            'argv': '-f -- 1 2'
        },
        'opt282': {
            'doc': '''\
Usage:
  selenium_prob_launcher.py [-v]

Options:
  -v, --verbose

Example:
  blabla alalal

Test for docopt issue #282 in docpie''',
        },
        'opt130': {
            'doc': '''\
Usage:
  check_snmp storage (-h | --help)
  check_snmp storage -w <warning> -c <critical>
      -H <host-address> -t <timeout>
      (--v2c -C <community> | -l <login> -x <passwd> -X <privpass> -L <protocols>)

Options:
  -h, --help
        Show this help message and exit.
  -H <host-address>, --host=<host-address>
        Set the address of the host.
  -t <timeout>, --timeout=<timeout>
        Set the timeout, in seconds, of the SNMP request.
  --v2c
        Use SNMP V2c instead of SNMP V3.
  -C <community>, --community=<community>
        Set the community password for SNMP V2c.
  -l <login>, --login=<login>
        Set the login for SNMP V3.
  -x <passwd>, --passwd=<passwd>
        Set the auth password for SNMP V3.
  -X <privpass>, --privpass=<privpass>
        Set the priv password for SNMP V3.
  -L <protocols>, --protocols=<protocols>
        Set the auth and priv protocols for SNMP V3. The authorised
        values are: "md5,des" "md5,aes" "sha,des" and "sha,aes".
  -w <warning>, --warning=<warning>
        With -w 80, the ckeck raises a warning if one local
        files system at least is full at more than 80%.
  -c <critical>, --critical=<critical>
        With -c 90, the ckeck raises a critical if one local
        files system at least is full at more than 90%.

Test for docopt issue #130 in docpie''',
            'argv': 'storage -w 80 -c 90 -H 127.0.0.1 -t 300 --v2c -C pwd',
        },
        'opt275': {
            'doc': '''\
usage:
  script foo <bar> [-v ...] [options]

Options:
  -v...                  increase verbosity

Test for docopt issue #275 in docpie''',
            'argv': 'foo asd -vvv',
        },
        'opt209': {
            'doc': '''\
usage: git [--version] [--exec-path=<path>] [--html-path]
           [-p|--paginate|--no-pager] [--no-replace-objects]
           [--bare] [--git-dir=<path>] [--work-tree=<path>]
           [-c <name>=<value>] [--help]
           <command> [<args>...]

options:
   -p, --paginate
   -h, --help

The most commonly used git commands are:
   add        Add file contents to the index
   branch     List, create, or delete branches
   checkout   Checkout a branch or paths to the working tree
   clone      Clone a repository into a new directory
   commit     Record changes to the repository
   push       Update remote refs along with associated objects
   remote     Manage set of tracked repositories

See 'git help <command>' for more information on a specific command.

Test docopt issue #209 in docpie''',
            'argv': 'checkout .',
        },
        'mycopy.py': {
            'doc': '''My copy script

Usage:
  cp.py [options] <source_file> <target_file>
  cp.py [options] <source_file>... <target_directory>

Options:
  -h -? --help    print this screen
  --version       print the version of this script
  -v --verbose    print more information while  running''',
            'argv': './docpie/*.py ./docpie/utest/*.py ~/my_project',
        },
        'attachopt': {
            'doc': 'Usage: prog -abc',
            'argv': '-a -bc',
        },
        'attachvalue': {
            'doc': '''\
Usage:
  prog [options]

Options:
  -a <value>  -a expects one value''',
            'argv': '-abc'
        },
        'testfile': {
            'doc': 'Usage: prog <file>',
            'argv': '-- --test',
        },
        'from_to': {
            'doc': '''\
Usage:
  program.py <from> <to>...
  program.py -s <source> <to>...''',
            'argv': '/home/* /tmp/1 /tmp/2'
        },
        'either_args': {
            'doc': 'Usage: prog (<a> | <b>)',
            'argv': 'docpie'
        },

        'same_name': {
            'doc': 'Usage: program.py <file> <file> --path=<path>...',
            'argv': 'file1 file2 --path ./here ./there'
        },
        'same_name_repeat_option': {
            'doc': 'Usage: program.py <file> <file> (--path=<path>)...',
            'argv': 'file1 file2 --path=./here --path=./there',
        },
        'non_posix_option': {
            'doc': '''\
Usage: prog [options]

Options:
-a..., --all ...               -a is countable
-b<sth>..., --boring=<sth>...  inf argument
-c <a> [<b>]                   optional & required args
-d [<arg>]                     optional arg''',
            'argv': '-aa -a -b go go go -c sth else',
        },
        'option_format': {
            'doc': '''\
Usage: [options]

Options:
-?, -h, --help  print help message. use
                -h/-? for a short help and
                --help for a long help.
-a, --all
    A long long long long long long long
    long long long long long description of
    -a & --all

Enjoy! Hope you like it!''',
            'argv': '-?'
        },
        'example_default': {
            'doc': '''\
Usage: [options]

Options:
    --coefficient=K  The K coefficient [default: 2.95]
    --output=FILE    Output file [default: ]
    --directory=DIR  Some directory [default:  ]
    --input=FILE     Input file. This default wont work [default: sys.stdout].
''',
        },
        'repeat_default': {
            'doc': '''\
Usage: my_program.py [--repeatable=<arg> --repeatable=<arg>]
                     [--another-repeatable=<arg>]...
                     [--not-repeatable=<arg>]

Options:
  --repeatable=<arg>          # will be ['./here', './there']
                              [default: ./here ./there]
  --another-repeatable=<arg>  # will be ['./here']
                              [default: ./here]
  --not-repeatable=<arg>      # will be './here ./there',
                              # because it is not repeatable
                              [default: ./here ./there]
''',
        },
        'docexample': {
            'doc': '''\
Usage: my_program.py [-hso FILE] [--quiet | --verbose] [INPUT ...]

Options:
 -h --help    show this
 -s --sorted  sorted output
 -o FILE      specify output file [default: ./test.txt]
 --quiet      print less text
 --verbose    print more text'''
        },
        'docpie': {
            'doc': '''\
Usage: my_program [-docpie]''',
            'argv': '-c -d -e'
        },
    }

    t = docpie.__timestamp__

    def get(self):
        example = self.get_argument('example', None)
        result = self.default
        result['file_name'] = 'pie.py'
        output = None
        if example:
            result.update(self.example[example])
        else:
            doc = self.get_argument('doc', None)
            result['doc'] = doc or None
            if doc:
                argv = self.get_argument('argv')
                result['argv'] = argv
                name = self.get_argument('name', None) or None
                config = {
                    'help': self.get_bool('help'),
                    # may be empty str
                    'version': self.get_argument('version', None) or None,
                    'stdopt': self.get_bool('stdopt'),
                    'attachopt': self.get_bool('attachopt'),
                    'attachvalue': self.get_bool('attachvalue'),
                    'auto2dashes': self.get_bool('auto2dashes'),
                    'name': name,
                    'case_sensitive': self.get_bool('case_sensitive'),
                    'optionsfirst': self.get_bool('optionsfirst'),
                    'appearedonly': self.get_bool('appearedonly')
                }

                if name is not None:
                    result['file_name'] = name

                with StdoutRedirect() as stdout:
                    args = shlex.split('pie.py ' + argv)
                    try:
                        # \r\n can not be handled correctly so far
                        # It's a bug
                        pie = docpie.docpie(doc.replace('\r\n', '\n'), args,
                                            **config)
                    except BaseException as e:
                        # in pypy3, sys.exit() gives e.args[0] = None
                        output = e.args[0] or ''
                    else:
                        output = str(pie)

                    if not output.strip():
                        output = stdout.read()

                result.update(config)

        if self.is_ajax():
            return self.write(json.dumps({'output': output}))

        return self.render(
            'project/docpie/try.html',
            version=docpie.__version__,
            time=self.get_time(),
            doc=result.pop('doc'),
            argv=result.pop('argv'),
            file_name=result.pop('file_name'),
            output=output,
            modified=self.diff_config(result),
            config=result,
            jsonlize=json.dumps
        )

    def get_time(self):
        if self.locale.code.startswith('en'):
            return time.ctime(self.t)
        return time.strftime('%m月%d日，%H:%M', time.localtime(self.t))

    @property
    def default(self):
        return {'doc': None, 'argv': None, 'help': True, 'version': None,
                'stdopt': True, 'attachopt': True, 'attachvalue': True,
                'auto2dashes': True, 'name': None, 'case_sensitive': False,
                'optionsfirst': False, 'appearedonly': False}  #, 'extra': {}}

    def diff_config(self, source):
        default = self.default
        default.pop('doc')
        default.pop('argv')
        result = {}
        for key, default_value in default.items():
            # logger.debug('%s = %s / %s', key, default_value, source[key])
            source_value = source[key]
            if default_value != source_value:
                if isinstance(source_value, StrType):
                    source_value = repr(source_value)
                result[key] = source_value

        return result
