"""
Usage:
    login [options] [--user=<user>] [--pwd=<pwd>]

Options:
    -u --user=<user>
    -p --pwd=<pwd>
    -l --local    local test
    -j --jolla    login to jolla
"""
import json
import logging
import requests
import sys
import os
from bs4 import BeautifulSoup

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

root = os.path.normpath(os.path.join(__file__, '..', '..', '..', '..'))
sys.path.insert(0, root)
from lib.tool import url
sys.path.pop(0)

logger = logging.getLogger('login')


def login_tomorrow(user, pwd, base, session=None):
    if session is None:
        session = requests.session()

    login = urljoin(base, 'login/')
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


def login_jolla(user, pwd, base, tbase, session=None):
    if session is None:
        session = requests.session()

    # get login auth link
    resp = session.get(urljoin(base, 'login/'), verify=False)
    soup = BeautifulSoup(resp.content, 'html5lib')
    link_tag = soup.find('a', {'class': 'site'})
    link = link_tag.get('href')

    # pre login: tomorrow
    session = login_tomorrow(user, pwd, tbase, session=session)

    # do login
    session.get(link, verify=False)

    logger.debug(
        session.get(
            urljoin(base, 'task/'),
            allow_redirects=False).status_code)

    return session


if __name__ == '__main__':
    import docpie
    import sys
    import os
    from requests.packages.urllib3.exceptions import InsecureRequestWarning

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..', '..')))
    from lib.tool.bashlog import stdoutlogger
    sys.path.pop(0)

    stdoutlogger(level=logging.DEBUG)

    logging.getLogger('docpie').setLevel(logging.CRITICAL)

    args = docpie.docpie(__doc__)
    user = args['--user']
    pwd = args['--pwd']

    if not user or not pwd:
        conf = os.path.normpath(os.path.join(__file__, '..', 'config.conf'))
        with open(conf, 'r', encoding='utf-8') as f:
            config = json.load(f)
        user = config['user']
        pwd = config['pwd']

    local = args['--local']
    to_jolla = args['--jolla']

    if to_jolla:
        if local:
            base = 'https://jolla.fake.today/'
            tbase = 'https://tomorrow.fake.today/'
        else:
            base = 'https://jolla.comes.today/'
            tbase = 'https://tomorrow.comes.today/'
        login_jolla(user, pwd, base, tbase)
    else:
        if local:
            base = 'https://tomorrow.fake.today/'
        else:
            base = 'https://tomorrow.comes.today/'
        login_tomorrow(user, pwd, base)
