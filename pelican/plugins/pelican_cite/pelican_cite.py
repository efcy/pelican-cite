# -*- coding: utf-8 -*-
"""
pelican-cite
==============

A Pelican plugin that provides a BibTeX-style reference system within
pelican sites.

Based on teh Pelican BibTeX plugin written by Vlad Niculae <vlad@vene.ro>
"""

import logging
import re
from typing import List

from pelican import signals
from pelican.contents import Article
from pelican.generators import ArticlesGenerator, PagesGenerator
from pybtex.backends import html
from pybtex.database import PybtexError
from pybtex.database.input.bibtex import Parser
from pybtex.plugin import find_plugin
from pybtex.style.formatting.unsrt import Style as UnsrtStyle

from .author_year import LabelStyle

logger = logging.getLogger(__name__)

JUMP_BACK = '<a class="cite-backref" href="#ref-{0}-{1}" title="Jump back to reference {1}">{2}</a>'
CITE_RE = re.compile(r"\[&#64;(&#64;)?\s*(\w.*?)\s*\]")


class Style(UnsrtStyle):
    name = "inline"
    default_sorting_style = "author_year_title"
    default_label_style = "author_year"

    def __init__(
        self,
        label_style=None,
        name_style=None,
        sorting_style=None,
        abbreviate_names=False,
        **kwargs
    ):
        super().__init__(
            label_style, name_style, sorting_style, abbreviate_names, **kwargs
        )
        self.name_style = find_plugin(
            "pybtex.style.names", name_style or self.default_name_style
        )()
        self.label_style = LabelStyle()
        self.sorting_style = find_plugin(
            "pybtex.style.sorting", sorting_style or self.default_sorting_style
        )()
        self.format_name = self.name_style.format
        self.format_labels = self.label_style.format_labels
        self.sort = self.sorting_style.sort
        self.abbreviate_names = abbreviate_names


global_bib = None

style = Style()
backend = html.Backend()


def get_bib_file(article: Article):
    """
    If a bibliography file is specified for this article/page, parse
    it and return the parsed object.
    """
    if "publications_src" in article.metadata:
        refs_file = article.metadata["publications_src"]
        try:
            local_bib = Parser().parse_file(refs_file)
            return local_bib
        except PybtexError as e:
            logger.warning(
                "`pelican_bibtex` failed to parse file %s: %s" % (refs_file, str(e))
            )
            return global_bib
    else:
        return global_bib


def process_content(article: Article):
    """
    Substitute the citations and add a bibliography for an article or
    page, using the local bib file if specified or the global one otherwise.
    """
    data = get_bib_file(article)
    if not data:
        return
    content: str = article._content
    content = content.replace("@", "&#64;")

    # Scan post to figure out what citations are needed
    cite_count = {}
    replace_count = {}
    for citation in CITE_RE.findall(content):
        if citation[1] not in cite_count:
            cite_count[citation[1]] = 1
            replace_count[citation[1]] = 1
        else:
            cite_count[citation[1]] += 1

    # Get formatted entries for the appropriate bibliographic entries
    cited = []
    for key in data.entries.keys():
        if key in cite_count:
            cited.append(data.entries[key])
    if len(cited) == 0:
        return
    formatted_entries = style.format_entries(cited)

    # Get the data for the required citations and append to content
    labels = {}
    content += "<hr>\n<h2>Bibliography</h2>\n"
    for formatted_entry in formatted_entries:
        key = formatted_entry.key
        ref_id = key.replace(" ", "")
        label = (
            "<a href='#"
            + ref_id
            + "' id='ref-"
            + ref_id
            + "-{0}'>"
            + formatted_entry.label
            + "</a>"
        )
        t = formatted_entry.text.render(backend)
        t = t.replace("\\{", "&#123;")
        t = t.replace("\\}", "&#125;")
        t = t.replace("{", "")
        t = t.replace("}", "")
        text = "<p id='" + ref_id + "'>" + t
        for i in range(cite_count[key]):
            if i == 0:
                text += " " + JUMP_BACK.format(ref_id, 1, "↩")
                if cite_count[key] > 1:
                    text += JUMP_BACK.format(ref_id, 1, " <sup>1</sup> ")
            else:
                text += JUMP_BACK.format(
                    ref_id, i + 1, "<sup>" + str(i + 1) + "</sup> "
                )
        text += "</p>"
        content += text + "\n"
        labels[key] = label

    # Replace citations in article/page
    cite_count = {}

    def replace_cites(match):
        label_ = match.group(2)
        if label_ in labels:
            if label_ not in cite_count:
                cite_count[label_] = 1
                replace_count[label_] = 1
            else:
                cite_count[label_] += 1
            lab = labels[label_].format(cite_count[label_])
            if "&#64;&#64;" in match.group():
                return lab
            else:
                m = re.search(r">\s*\(\s*(.*?),\s*(.*?)\s*\)\s*<", lab)
                lab = (
                    lab[0 : m.start()]
                    + ">"
                    + m.group(1)
                    + " ("
                    + m.group(2)
                    + ")<"
                    + lab[m.end() :]
                )
                return lab
        else:
            logger.warning('No BibTeX entry found for key "{}"'.format(label_))
            return match.group(0)

    content = CITE_RE.sub(replace_cites, content)
    article._content = content


def add_citations(generators: List[ArticlesGenerator, PagesGenerator]):
    global global_bib

    if "PUBLICATIONS_SRC" in generators[0].settings:
        refs_file = generators[0].settings["PUBLICATIONS_SRC"]
        try:
            global_bib = Parser().parse_file(refs_file)
        except PybtexError as e:
            logger.warning(
                "`pelican_bibtex` failed to parse file %s: %s" % (refs_file, str(e))
            )

    # Process the articles and pages
    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            articles = generator.articles + generator.translations + generator.drafts
            for article in articles:
                process_content(article)
        elif isinstance(generator, PagesGenerator):
            for page in generator.pages:
                process_content(page)


def register():
    signals.all_generators_finalized.connect(add_citations)
