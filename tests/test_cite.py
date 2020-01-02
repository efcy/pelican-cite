from copy import deepcopy
from typing import List, Match, Optional

from bs4 import BeautifulSoup
from pelican.contents import Article
from pelican_cite import (
    CITE_RE,
    ArticleCite,
    CitationsProcessor,
    Style,
    _find_cites_in_article,
)
from pybtex.database import BibliographyData, Entry, Person
from pybtex.richtext import String, Text
from pybtex.style import FormattedEntry
from pybtex.utils import OrderedCaseInsensitiveDict
import pytest


@pytest.fixture()
def formatted_entry() -> FormattedEntry:
    return FormattedEntry(key="abc", text=Text(String("Einstein")), label="abc")


@pytest.fixture()
def entry() -> Entry:
    return Entry("misc", persons={"author": [Person(last="Einstein")]})


@pytest.mark.parametrize(
    "md_input,expected",
    [
        ("[&#64;Bai2011]", (None, "Bai2011")),
        ("[&#64;  Bai2011]", (None, "Bai2011")),
        ("[&#64;&#64;Bai2011]", ("&#64;", "Bai2011")),
    ],
)
def test_cite_re(md_input: str, expected: List[Optional[str]]):
    match: Optional[Match[str]] = CITE_RE.match(md_input)
    assert match.groups() == expected


def test_process_content(monkeypatch, articles_generator, get_global_bib_mock):
    article_content = """
    Something above
    [@abc]
    Something below
    """
    article = Article(article_content)
    articles_generator.articles = [
        article,
    ]

    processor = CitationsProcessor([articles_generator])
    processor._process_article_content(article)


def test_find_cites_in_article__single_cite_in_article(style, formatted_entry, entry):
    article_content = """
    Something above
    [&#64;abc]
    Something below
    """
    entries = {"abc": deepcopy(entry)}
    formatted_entries = style.format_entries(entries.values())
    bib = BibliographyData(entries=entries)
    cites = _find_cites_in_article(article_content, bib, style)

    assert cites == [ArticleCite(next(formatted_entries))]


def test_find_cites_in_article__multiple_cites_in_article(
    entry, style, formatted_entry
):
    article_content = """
    Something above
    [&#64;abc]
    Something below
    [&#64;abc]
    [&#64;abcd]
    """
    entries = {"abc": deepcopy(entry), "abcd": deepcopy(entry)}
    formatted_entries = style.format_entries(entries.values())
    bib = BibliographyData(entries=entries)
    cites = _find_cites_in_article(article_content, bib, style)

    assert cites == [
        ArticleCite(next(formatted_entries), count=2),
        ArticleCite(next(formatted_entries), count=1),
    ]


def test_find_cites_in_article__no_cites_in_article(entry, style, formatted_entry):
    article_content = """
    Something above
    Something below
    """
    entries = OrderedCaseInsensitiveDict([("abc", entry)])

    bib = BibliographyData(entries=entries)
    style = Style()

    cites = _find_cites_in_article(article_content, bib, style)

    assert cites == []


def test_find_cites_in_article__cite_not_in_bib(logger_warning_mock, style):
    article_content = """
    Something above
    [&#64;abc]
    Something below
    """
    entries = OrderedCaseInsensitiveDict([])
    bib = BibliographyData(entries=entries)
    cites = _find_cites_in_article(article_content, bib, style)

    logger_warning_mock.assert_called_once_with('No BibTeX entry found for key "abc"')
    assert cites == []


def test_render_bibliography__single_cite(cite_relativity_theory, cite_html):
    cite_relativity_theory.count = 1
    rendered = cite_html.render_bibliography([cite_relativity_theory])
    html = BeautifulSoup(rendered, "html.parser")

    assert html.ol.li["id"] == "einrelt"
    assert html.ol.li.a.sup.i.b.text.strip() == "1"


def test_render_bibliography__same_cite_used_multiple_times(
    cite_relativity_theory, cite_html
):
    cite_relativity_theory.count = 3
    rendered = cite_html.render_bibliography([cite_relativity_theory])
    html = BeautifulSoup(rendered, "html.parser")

    assert html.ol.li["id"] == "einrelt"

    links = html.ol.li.findAll("a")
    assert len(links) == 3
    assert links[0].sup.i.b.text.strip() == "1"
    assert links[2].sup.i.b.text.strip() == "3"


def test_render_bibliography__multiple_cites(
    cite_relativity_theory, cite_universe_in_a_nutshell, cite_html
):
    cite_relativity_theory.count = 3
    cite_universe_in_a_nutshell.count = 2
    rendered = cite_html.render_bibliography(
        [cite_relativity_theory, cite_universe_in_a_nutshell]
    )
    html = BeautifulSoup(rendered, "html.parser")

    citations = html.ol.findAll("li")
    assert len(citations) == 2

    assert citations[0]["id"] == "einrelt"
    einstein_links = citations[0].findAll("a")
    assert len(einstein_links) == 3
    assert einstein_links[0].sup.i.b.text.strip() == "1"
    assert einstein_links[2].sup.i.b.text.strip() == "3"

    assert citations[1]["id"] == "hawuian"
    hawking_links = citations[1].findAll("a")
    assert len(hawking_links) == 2
    assert hawking_links[0].sup.i.b.text.strip() == "1"
    assert hawking_links[1].sup.i.b.text.strip() == "2"
