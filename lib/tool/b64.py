import base64
from sys import version_info

py3 = version_info[0] >= 3


def decode_data_url(data_url):
    _, data64 = data_url.split(',', 1)
    if py3:
        data64 = data64.encode()
    return base64.b64decode(data64)


def gen_data_url(content, format='image/gif', is_byte=False):
    if not is_byte:
        content = content.encode('utf-8')
    return 'data:image/gif;base64,' + base64.b64encode(content).decode('utf-8')
