'''a small Python 2 and 3 compatibility library'''

import os
import sys
# get version
py3 = (sys.version_info[0] == 3)
py2 = (not py3)

# Note: avoid using 'x' mode when in py2 & pypy3
# open
if not py3:
    import codecs
    import warnings
    import os

    class FileExistsError(OSError):
        pass

    def open(file, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None, closefd=True, opener=None):

        if newline is not None:
            warnings.warn('newline is not supported in py2')
        if not closefd:
            warnings.warn('closefd is not supported in py2')
        if opener is not None:
            warnings.warn('opener is not supported in py2')

        if 'x' in mode and os.path.exists(file):
            raise FileExistError("[Errno 17] File exists: '%s'" % file)

        return codecs.open(filename=file, mode=mode, encoding=encoding,
                           errors=errors, buffering=buffering)
else:
    try:
        FileExistsError
        FileNotFoundError
    except NameError:  # pypy3

        class FileExistsError(OSError):
            pass

        class FileNotFoundError(IOError):
            pass

        def open(file, mode='r', *a, **k):
            if 'x' in mode:
                if os.path.exists(file):
                    raise FileExistError("[Errno 17] File exists: '%s'" % file)
                mode = mode.replace('x', 'w')  # pypy3 does not support 'x'
            elif 'r' in mode:
                if not os.path.exists(file):
                    raise FileNotFoundError(
                        "[Errno 2] No such file or directory: '%s'" % file)

            return __builtins__.open(file, mode, *a, **k)
    else:
        FileExistsError = FileExistsError  # for import
        FileNotFoundError = FileNotFoundError  # for import
        open = open     # for import
