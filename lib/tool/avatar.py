try:
    from io import BytesIO
except ImportError:
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO

import pagan


def gen_avatar(inpt):
    with BytesIO() as output:
        img = pagan.generator.generate(inpt, pagan.generator.HASH_MD5)
        # img = pagan.generator.generate(inpt, lambda x: x)
        img.save(output, format='PNG')
        return output.getvalue()

if __name__ == '__main__':
    print(gen_avatar('test'))
