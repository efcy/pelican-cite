pelican-cite
==============

Allows the use of BibTeX citations within a Pelican site.


Installation
============

To install simply run `pip install pelican-cite` and add it to the `PLUGINS` section of `pelicanconf.py`

```python
PLUGINS = [
    '...',
    'pelican.plugins.cite'
    '...',
]
```


## How to Use

This plugin reads a user-specified BibTeX file and generates bibliographic
information within your articles and pages.

If the file is present and readable, then content will be scanned for references
to citation keys. These take the format `[@Bai2011]` or `[@@Bai2011]`. These
will be replaced by incline citations which provide links to the full
bibliographic information at the end of the article. The former reference would
be replaced by a citation of the form "Bai & Stone (2011)", while the latter
would be replaced by "(Bai & Stone, 2011)".

If a citation key is used which does not exist within the BibTeX file then
a warning will be displayed.

### Configuration

#### `PUBLICATIONS_SRC`

Location of the BibTeX file.

The BibTeX file may, optionally, be provided or overridden on a per-article
basis by supplying the meta-data `publications_src`.

The BibTeX file may, optionally, be provided or overridden on a per-article
basis by supplying the meta-data `publications_src`.

#### `BIBLIOGRAPHY_HEADER`

Html code for the headers shown for the bibliography on each article or page.

Default to

```html
<hr><h2>Bibliography</h2>
```

#### `BIBLIOGRAPHY_NAME_STYLE`

Defines how names will be formatted in the output.
Styles included in `"Pybtex"` are `"plain"` and `"lastfirst"`. Defaults to `None`.

#### `BIBLIOGRAPHY_LABEL_STYLE`

Defines how the labels will be formatted in the output.

~~Styles included in `Pybtex` are `"alpha"` and `"number"`. Defaults to `"alpha"`~~

> At this moment only `"author_year"` is supported!

There is also a custom style available called `"author_year"`.
You can use this by installing it with `pip install pybtex-author-year-label`.

#### `BIBLIOGRAPHY_SORTING_STYLE`

Defines how the bibliography will be sorted.
Styles included in `Pybtex` are `"author_year_title"` and `"none"`. Defaults to `"author_year_title"`

## Attribution
`pelican-cite` is based on the
[pelican-bibtex](https://github.com/vene/pelican-bibtex) plugin written by
[Vlad Niculae](https://github.com/vene)
and [pelican-cite](https://github.com/cmacmackin/pelican-cite) written by
[Chris MacMackin](https://github.com/cmacmackin).
