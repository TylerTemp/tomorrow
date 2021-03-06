import base64
import uuid
import sys
import re

__all__ = ['generate']
py3 = (sys.version_info[0] >= 3)


def generate():
    result = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
    if py3:
        result = result.decode('utf-8')
    return re.sub(r'[/#=?%\+]', '-', result)

if __name__ == '__main__':
    print(generate())
