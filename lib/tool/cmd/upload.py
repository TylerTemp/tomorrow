"""
Usage:
    upload [options] (<dir> | <file>)...

Options:
    -b, --bucket=<name>    [default: jolla]
    -p, --prefix=<name>
    -k, --key=<key>
    -s, --secret=<secret>
"""

import qiniu
import qiniu.config
import logging

logger = logging.getLogger('upload')

CLIENT = None
KEY = None
SECRET = None
BUCKET = 'jolla'


def get_client():
    global CLIENT
    if CLIENT is None:
        CLIENT = qiniu.Auth(KEY, SECRET)

    return CLIENT


def set_client(key, secret):
    global KEY
    global SECRET
    global CLIENT
    KEY = key
    SECRET = secret
    CLIENT = qiniu.Auth(KEY, SECRET)
    return CLIENT


def upload(data, name=None, bucket=None):
    if bucket is None:
        bucket = BUCKET

    client = get_client()
    token = client.upload_token(bucket, name, 3600)

    ret, info = qiniu.put_data(token, name, data)
    return ret['key']


if __name__ == '__main__':
    import json
    import os

    conf = os.path.normpath(os.path.join(__file__, '..', 'config.conf'))
    with open(conf, 'r', encoding='utf-8') as f:
        config = json.load(f)

    app = config['qiniu']
    KEY = app['key']
    SECRET = app['secret']
    # bucket = get_bucket('jolla')
    # with open(conf, 'r', encoding='utf-8') as f:
    #     print(upload(bucket, conf, 'test/test.conf'))
    with open(conf, 'r', encoding='utf-8') as f:
        print(upload(f.read(), 'test/test.conf'))
