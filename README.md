pelican-cite
==============

Allows the use of BibTeX citations within a Pelican site. This plugin is based on the
[pelican-bibtex](https://github.com/vene/pelican-bibtex) plugin written by
[Vlad Niculae](https://github.com/vene)
and [pelican-cite](https://github.com/cmacmackin/pelican-cite) written by
[Chris MacMackin](https://github.com/cmacmackin) and aims to improve the following points:

- More flexibility using configuration
    - The user can use any label, soring and naming style
    - The user can create their own Jinja2 template for bibliography and label (This is still a TODO)
- Better maintainability
- Everything is tested with PyTest


Installation
============

To install simply run `pip install pelican-cite` and add it to the `PLUGINS` section of `pelicanconf.py`

```python
PLUGINS = [
    '...',
    'pelican_cite'
    '...',
]
```


## How to Use

This plugin reads a user-specified BibTeX file and generates bibliographic
information within your articles and pages.

If the file is present and readable, then content will be scanned for references
to citation keys. These take the format `[@Bai2011]`.
The format `[@@Bai2011]` is also possible for backwards compatibility with [pelican-cite](https://github.com/cmacmackin/pelican-cite) by
[Chris MacMackin](https://github.com/cmacmackin).

If a citation key is used which does not exist within the BibTeX file then
a warning will be displayed.

### Configuration

#### `PUBLICATIONS_SRC`

Location of the BibTeX file.

The BibTeX file may, optionally, be appended on a per-article
basis by supplying the meta-data `publications_src`.

#### `BIBLIOGRAPHY_NAME_STYLE`

Defines how names will be formatted in the output.
Styles included in `"Pybtex"` are `"plain"` and `"lastfirst"`. Defaults to `None`.

#### `BIBLIOGRAPHY_LABEL_STYLE`

Defines how the labels will be formatted in the output.

Styles included in `Pybtex` are `"alpha"` and `"number"`. Defaults to `"alpha"`

##### Author_year label style

There is also a custom style available called `"author_year_1"` and `"author_year_2"`.
The first will show labels like `(Author,year)`, the second will show labels like `Author (year)`

You can use this by installing it with `pip install pybtex-author-year-label`.

#### `BIBLIOGRAPHY_SORTING_STYLE`

Defines how the bibliography will be sorted.
Styles included in `Pybtex` are `"author_year_title"` and `"none"`. Defaults to `"author_year_title"`

### Usage in Pelican template

#### Labels

Labels are rendered with the `BIBLIOGRAPHY_LABEL_STYLE` setting, and you cannot set anything
in the template.

#### Bibliography

##### Use out of the box template

You can add the bibliography anywhere in your template.
`pelican_cite` comes with a rendered bibliography out of the box. Simply add the following to your template:

```jinja2
{% if article.bibliography %}
    {{ article.bibliography.rendered }}
{% endif %}
```

This will use the template from `pelican_cite/templates/citations.html` to render a bibliography

##### Create your own template

You can also create your own template. To do this `article.bibliography` has a `cites` attribute.

Attribute | Description
---|---
`article.bibliography.cites.cite_key` | The id you used for the citation in your `.bib` file.
`article.bibliography.cites.ref_id` | The `cite_key`, without spaces.
`article.bibliography.cites.rendered_entry` | A rendered string containing the citation.
`article.bibliography.cites.count` | The number of times the entry was cited in the article.

Here is a template to get you started:

```jinja2
{% if article.bibliography %}
<div id="citations">
    <hr>
    <h3>Citations</h3>
    <ol class="references">
        {% for cite in article.bibliography.cites %}
            <li id="{{ cite.ref_id }}">
                <span class="reference-text">{{ cite.rendered_entry }}</span>
                {% for i in range(1, cite.count + 1) %}
                    <a class="cite-backref" href="#ref-{{ cite.ref_id }}-{{ i }}"
                       title="Jump back to reference {{ i }}">
                        <sup>
                            <i>
                                <b>
                                    {{ i }}
                                </b>
                            </i>
                        </sup>
                    </a>
                {% endfor %}
            </li>
        {% endfor %}
    </ol>
</div>
{% endif %}
```
