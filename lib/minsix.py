'''a small Python 2 and 3 compatibility library'''

import sys
# get version
py3 = (sys.version_info[0] == 3)
py2 = (not py3)

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
    open = open     # for import
    FileExistsError = FileExistsError    # for import
