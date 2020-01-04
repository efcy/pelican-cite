# -*- coding: utf-8 -*-
"""
pelican-cite
==============

A Pelican plugin that provides a BibTeX-style reference system within
pelican sites.

Based on teh Pelican BibTeX plugin written by Vlad Niculae <vlad@vene.ro>
"""
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
import logging
import os
import re
from typing import Dict, List, Match, Union

from jinja2 import Environment, FileSystemLoader
from pelican import Pelican, signals
from pelican.contents import Article, Page
from pelican.generators import ArticlesGenerator, PagesGenerator
from pybtex.backends import html
from pybtex.database import BibliographyData, Entry, PybtexError
from pybtex.database.input.bibtex import Parser
from pybtex.plugin import find_plugin
from pybtex.style import FormattedEntry
from pybtex.style.formatting.unsrt import Style as UnsrtStyle

logger = logging.getLogger(__name__)

CITE_RE = re.compile(r"\[&#64;(&#64;)?\s*(\w.*?)\s*\]")

_PUBLICATIONS_SRC = "PUBLICATIONS_SRC"
_BIBLIOGRAPHY_NAME_STYLE = "BIBLIOGRAPHY_NAME_STYLE"
_BIBLIOGRAPHY_LABEL_STYLE = "BIBLIOGRAPHY_LABEL_STYLE"
_BIBLIOGRAPHY_SORTING_STYLE = "BIBLIOGRAPHY_SORTING_STYLE"


def setup_cite(pelican: Pelican):
    """Setup the default settings."""
    pelican.settings.setdefault(_PUBLICATIONS_SRC, None)
    pelican.settings.setdefault(_BIBLIOGRAPHY_NAME_STYLE, None)
    pelican.settings.setdefault(_BIBLIOGRAPHY_LABEL_STYLE, "alpha")
    pelican.settings.setdefault(_BIBLIOGRAPHY_SORTING_STYLE, "author_year_title")


class Style(UnsrtStyle):
    name = "inline"

    def __init__(
        self,
        label_style=None,
        name_style=None,
        sorting_style=None,
        abbreviate_names=False,
        **kwargs,
    ):
        super().__init__(
            label_style, name_style, sorting_style, abbreviate_names, **kwargs
        )

        self.name_style = find_plugin("pybtex.style.names", name_style)()
        self.label_style = find_plugin("pybtex.style.labels", label_style)()
        self.sorting_style = find_plugin("pybtex.style.sorting", sorting_style)()
        self.format_name = self.name_style.format
        self.format_labels = self.label_style.format_labels
        self.sort = self.sorting_style.sort
        self.abbreviate_names = abbreviate_names

    def __str__(self) -> str:
        return (
            f"label_style: {self.label_style}, "
            f"name_style: {self.name_style}, "
            f"sorting_style: {self.sorting_style}, "
            f"abbreviate_names: {self.abbreviate_names}"
        )


@dataclass
class ArticleCite:
    """class to contain citation information for an Article or page"""

    def __init__(self, formatted_entry: FormattedEntry, count: int = 1):
        self.formatted_entry = formatted_entry
        self.count = count

    def __repr__(self) -> str:
        return f"cite_key: {self.cite_key}, " f"count: {self.count}, "

    @property
    def rendered_entry(self) -> str:
        """Rendered entry as it will be used in the bibliography,
        without back references"""
        return (
            self.formatted_entry.text.render(html.Backend())
            .replace("\\{", "&#123;")
            .replace("\\}", "&#125;")
            .replace("{", "")
            .replace("}", "")
        )

    @property
    def rendered_label(self) -> str:
        """Rendered label (without html)"""
        return self.formatted_entry.label

    @property
    def cite_key(self) -> str:
        """Original cite key as it is used in the .bib file"""
        return self.formatted_entry.key

    @property
    def ref_id(self) -> str:
        """Cite key without white spaces"""
        return self.cite_key.replace(" ", "")


class CiteHtml:
    def __init__(self):
        loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"))
        env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

        self.bibliography_template = env.get_template("citations.html")
        self.label_template = env.get_template("label.html")

    def render_bibliography(self, cites: List[ArticleCite]) -> str:
        return self.bibliography_template.render(cites=cites)

    def render_label(self, cite: ArticleCite, cite_count: int):
        return self.label_template.render(
            ref_id=cite.ref_id,
            cite_count=cite_count,
            rendered_label=cite.rendered_label,
        )


def _find_cites_in_article(
    article_content: str, bib_data: BibliographyData, style: Style
) -> List[ArticleCite]:
    cite_keys = CITE_RE.findall(article_content)

    entries: List[Entry] = []
    for cite_key in cite_keys:
        cite_key = cite_key[1]
        if cite_key not in bib_data.entries:
            logger.warning(f'No BibTeX entry found for key "{cite_key}"')
        else:
            entries.append(bib_data.entries[cite_key])

    formatted_entries = [e for e in style.format_entries(entries)]

    cites: Dict[str, ArticleCite] = dict()
    for entry in entries:
        if entry.key in cites:
            cites[entry.key].count += 1
        else:
            formatted_entry = next(e for e in formatted_entries if e.key == entry.key)
            cites[entry.key] = ArticleCite(formatted_entry)

    return [cite for cite in cites.values()]


def _replace_cites(content: str, cites: List[ArticleCite]):
    cite_html = CiteHtml()
    cite_count = Counter()

    def replace_cite(match: Match) -> str:
        cite_key = match.group(2)
        cite = next((c for c in cites if c.cite_key == cite_key), None)

        if cite is None:
            logger.error(f"replacing cite: {cite_key}")
            return match.group(0)

        cite_count[cite_key] += 1
        return cite_html.render_label(cite, cite_count[cite_key])

    return CITE_RE.sub(replace_cite, content)


def _get_global_bib(
    generator: Union[ArticlesGenerator, PagesGenerator]
) -> BibliographyData:
    refs_file = generator.context.get(_PUBLICATIONS_SRC)
    try:
        return Parser().parse_file(refs_file)
    except PybtexError as e:
        logger.warning(
            "`pelican_cite` failed to parse file %s: %s" % (refs_file, str(e))
        )


class CitationsProcessor:
    def __init__(self, generators: List[Union[ArticlesGenerator, PagesGenerator]]):
        self.generators = generators
        self.style: Style = Style(
            generators[0].context.get(_BIBLIOGRAPHY_LABEL_STYLE),
            generators[0].context.get(_BIBLIOGRAPHY_NAME_STYLE),
            generators[0].context.get(_BIBLIOGRAPHY_SORTING_STYLE),
        )
        self.global_bib: BibliographyData = _get_global_bib(generators[0])
        self.cite_html = CiteHtml()

        logger.info(f"Processing citations with style {self.style}")

    def process(self):
        # Process the articles and pages
        for generator in self.generators:
            if isinstance(generator, ArticlesGenerator):
                articles = (
                    generator.articles + generator.translations + generator.drafts
                )
                for article in articles:
                    self._process_article_content(article)
            elif isinstance(generator, PagesGenerator):
                for page in generator.pages:
                    self._process_article_content(page)

    def _get_bib(self, article: Article) -> BibliographyData:
        # TODO Test this method
        if "publications_src" not in article.metadata:
            return self.global_bib

        refs_file = article.metadata["publications_src"]
        try:
            local_bib = Parser().parse_file(refs_file)

            global_bib_copy = deepcopy(self.global_bib)
            global_bib_copy.add_entries(local_bib.entries)
            return global_bib_copy
        except PybtexError as e:
            logger.warning(
                "`pelican_bibtex` failed to parse file %s: %s" % (refs_file, str(e))
            )
            return self.global_bib

    def _process_article_content(self, article: Union[Article, Page]):
        """
        Substitute the citations and add a bibliography for an article or
        page, using the local bib file if specified or the global one otherwise.
        """
        bib = self._get_bib(article)

        if not bib:
            return

        # noinspection PyProtectedMember
        article_content: str = article._content.replace("@", "&#64;")
        article_cites = _find_cites_in_article(article_content, bib, self.style)
        logger.info(f"cites found: {article_cites}")

        if len(article_cites) == 0:
            return

        article._content = _replace_cites(article_content, article_cites)
        article.bibliography = dict()
        article.bibliography["rendered"] = self.cite_html.render_bibliography(
            article_cites
        )
        article.bibliography["cites"] = article_cites


def add_citations(generators):
    processor = CitationsProcessor(generators)
    processor.process()


def register():
    signals.initialized.connect(setup_cite)
    signals.all_generators_finalized.connect(add_citations)
