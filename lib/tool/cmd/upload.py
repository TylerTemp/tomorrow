"""
Usage:
    upload [options] (<dir> | <file>)...

Options:
    -p, --prefix=<name>    format: <bucket>/<dir>/
                           [default: jolla]
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
    from docpie import docpie

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('docpie').setLevel(logging.CRITICAL)

    args = docpie(__doc__)
    key = args['--key']
    sec = args['--secret']
    bucket_with_dir = args['--prefix']
    assert bucket_with_dir

    if not (key and sec):
        conf = os.path.normpath(os.path.join(__file__, '..', 'config.conf'))
        with open(conf, 'r', encoding='utf-8') as f:
            config = json.load(f)['qiniu']
        key = config['key']
        sec = config['secret']

    logger.debug('key: %s; secret: %s', key, sec)
    set_client(key, sec)

    bucket, _, prefix = bucket_with_dir.partition('/')
    if not prefix:
        prefix = None

    f_list = set()
    for each in args['<dir>']:
        if os.path.isdir(each):
            logger.info('find dir %s', each)
            base, dirs, files = next(os.walk(each))
            f_list.update(os.path.join(base, x) for x in files)

        else:
            logger.info('find file %s', each)
            f_list.add(each)

    logger.info(f_list)
    finished = []

    for each in f_list:
        logger.info('updating %s', each)
        name = prefix + os.path.split(each)[-1]

        with open(each, 'rb') as f:
            key = upload(f.read(), name, bucket)
            logger.info(key)
        if bucket == 'jolla':
            finished.append('https://dn-jolla.qbox.me/%s' % key)
            logger.info(finished[-1])

    for link in finished:
        print(link)
