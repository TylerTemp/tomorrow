try:
    from urllib.parse import urlparse, parse_qs, urlencode
except ImportError:
    from urlparse import urlparse, parse_qs
    from urllib import urlencode


def get_query(url):
    parsed = urlparse(url)
    return parsed.query


def decode_query(url, multi=False):
    result = parse_qs(get_query(url))

    if not multi:
        r = {}
        for k, v in result.items():
            assert len(v) == 1
            r[k] = v[0]
        return r

    return result


def encode_query(query):
    return urlencode(query)


if __name__ == '__main__':
    url = ('http://alice:secret@www.hostname.com:80'
           '/%7Ealice/python.cgi?query=text#sample')

    print(url)
    de = decode_query(url)
    print(de)
    de.update({'a': 'a', 'b': ['b', 'b2']})
    print(encode_query(de))
