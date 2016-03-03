"""
Usage:
    login <user> <pwd> <site>
"""
import json
import logging
import requests

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

logger = logging.getLogger('login')


def login_tomorrow(user, pwd, site=None, session=None):
    if session is None:
        session = requests.session()

    login = urljoin(site, 'login/')
    logger.info('log in： %s', login)
    get = session.get(login, verify=False)
    logger.info(get)

    para = {'user-or-email': user, 'pwd': pwd,
            '_xsrf': session.cookies.get('_xsrf')}
    response = session.post(
        login, data=para, verify=False,
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )

    result = json.loads(response.text)
    logger.info(result)

    assert not result['error']

    return session


if __name__ == '__main__':
    import docpie
    import sys
    import os

    sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..', '..')))
    from lib.tool.bashlog import stdoutlogger
    sys.path.pop(0)

    stdoutlogger(level=logging.DEBUG)

    logging.getLogger('docpie').setLevel(logging.CRITICAL)

    args = docpie.docpie(__doc__)
    user = args['<user>']
    pwd = args['<pwd>']
    site = args['<site>']

    if site in ('tomorrow', None):
        site = 'https://tomorrow.comes.today'
    if not site.endswith('/'):
        site += '/'
    if not site.startswith('https://'):
        site = 'https://' + site

    func = login_tomorrow

    func(user, pwd, site=site)
