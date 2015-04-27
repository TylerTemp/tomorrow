import bleach
import html2text

import markdown
import markdown_newtab
# from ..markdown_gridtables import mdx_grid_tables

__all__ = ['md2html', 'html2md', 'escape']

extend = (
    # define attributes, {: #someid .someclass somekey='some value' }
    # 'markdown.extensions.attr_list',
    # use fenced code block by 3 back quotes
    'markdown.extensions.fenced_code',
    # footnotes, text[^name]\n\n[^name] explain
    'markdown.extensions.footnotes',
    'markdown.extensions.tables',
    # new line to <br />
    # 'markdown.extensions.nl2br',
    # code highlight, and <pre></pre> added
    'markdown.extensions.codehilite',
    # ++text++ for <ins>text</ins> and ~~text~~ for <del>text</del>
    'del_ins',
    # add '_blank' for links
    markdown_newtab.makeExtension(),
    # table extend
    # mdx_grid_tables.makeExtension(),
    # replace <<, >> , ..., ect to HTML entity equivalents
    # 'markdown.extensions.smarty',
    # add menu in table at the head
    # 'markdown.extensions.toc',
    # convert any [[text]] to <a href="/text/" class="wikilink">text</a>
    # 'markdown.extensions.wikilinks',
)

# 'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
# 'i', 'li', 'ol', 'strong', 'ul'
white_tags = list(bleach.ALLOWED_TAGS)
white_tags.extend(('span', 'table', 'tr', 'td', 'th',
                   'ins', 'del', 'center', 'pre', 'u',
                   'h2', 'h3', 'h4', 'h5', 'h6',
                   'video'))

attributes = {'*': ('href', 'src', 'title', 'name', 'alt', 'height', 'length'
                    'border', 'text-align')}

_md = markdown.Markdown(smart_emphasis=False, safemode=False,
                        output_format='html5', extensions=extend)

md2html = _md.convert
# def md2html(md, smart_emphasis=False, safemode=False, extensions=None):
#     if extensions is None:
#         extensions = extend
#     return markdown.markdown(md, output_format='html5',
#                              smart_emphasis=smart_emphasis,
#                              safemode=safemode,
#                              extensions=extensions)

_parser = html2text.HTML2Text()
_parser.body_width = 0
html2md = _parser.handle


def escape(content):
    return bleach.clean(content, tags=white_tags, attributes=attributes)


if __name__ == '__main__':
    src = '''
# hello

++there++

~~am~~

**a** _simple_ __simple__ *test*

mark | down
-----|-----
to   | html

test

```python
import sys
sys.exit()
```
'''
    html = md2html(src)
    md = html2md(html)
    print(html)
    print('')
    print(md)
