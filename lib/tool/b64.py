import base64
from sys import version_info

py3 = version_info[0] >= 3


def decode_data_url(data_url):
    _, data64 = data_url.split(',', 1)
    if py3:
        data64 = data64.encode()
    return base64.b64decode(data64)