from bs4 import BeautifulSoup
from pelican.contents import Article
from pelican_cite import CitationsProcessor


def test_process_without_cites(articles_generator, get_global_bib_mock):
    article_text = f"""
    <h1>Something about Relativity</h1>
    <p>There is this nothing about Relativity</p>
    """
    article = Article(article_text)
    articles_generator.articles.append(article)

    processor = CitationsProcessor([articles_generator])
    processor.process()

    assert hasattr(article, "bibliography") is False


def test_process_single_cite(
    articles_generator,
    entry_relativity_theory,
    key_relativity_theory,
    get_global_bib_mock,
):
    article_text = f"""
    <h1>Something about Relativity</h1>
    <p>There is this thing about Relativity[@{key_relativity_theory}]</p>
    """
    article = Article(article_text)
    articles_generator.articles.append(article)

    processor = CitationsProcessor([articles_generator])
    processor.process()

    bibliography = article.bibliography

    soup = BeautifulSoup(bibliography["rendered"], "html.parser")
    assert soup.find(id="citations") is not None
    assert bibliography["cites"] is not None


def test_process_single_cite_used_multiple_times(
    articles_generator,
    entry_relativity_theory,
    key_relativity_theory,
    get_global_bib_mock,
):
    article_text = f"""
    <h1>Something about Relativity</h1>
    <p>There is this thing about Relativity[@{key_relativity_theory}]</p>
    <p>And something more[@{key_relativity_theory}]</p>
    """
    article = Article(article_text)
    articles_generator.articles.append(article)

    processor = CitationsProcessor([articles_generator])
    processor.process()

    bibliography = article.bibliography

    soup = BeautifulSoup(bibliography["rendered"], "html.parser")

    assert bibliography["cites"] is not None

    citations = soup.find(id="citations")
    assert citations is not None

    # There should be only one cite
    items = citations.ol.findAll("li")
    assert len(items) == 1

    # The cite is from the relativity theory entry
    citation = citations.ol.find(id=key_relativity_theory.replace(" ", ""))
    assert citation is not None

    # And it is referenced twice
    back_links = citation.findAll("a")
    assert len(back_links) == 2


def test_process_multiple_cites_in_article(
    articles_generator,
    entry_relativity_theory,
    entry_universe_in_a_nutshell,
    key_relativity_theory,
    key_universe_in_a_nutshell,
    get_global_bib_mock,
):
    article_text = f"""
    <h1>Something about Relativity</h1>
    <p>There is this thing about Relativity[@{key_relativity_theory}]</p>
    <p>And something more[@{key_relativity_theory}]</p>
    <p>But we should also mention the universe[@{key_universe_in_a_nutshell}]</p>
    """
    article = Article(article_text)
    articles_generator.articles.append(article)

    processor = CitationsProcessor([articles_generator])
    processor.process()

    bibliography = article.bibliography
    assert bibliography["cites"] is not None

    soup = BeautifulSoup(bibliography["rendered"], "html.parser")
    citations = soup.find(id="citations")
    assert citations is not None

    # There should be two cites
    items = citations.ol.findAll("li")
    assert len(items) == 2

    # The cite is from the relativity theory entry
    relativity_theory_citation = citations.ol.find(
        id=key_relativity_theory.replace(" ", "")
    )
    assert relativity_theory_citation is not None

    # Relativity theory it is referenced twice
    relativity_theory_back_links = relativity_theory_citation.findAll("a")
    assert len(relativity_theory_back_links) == 2

    # The second cite is about the universe
    universe_citation = citations.ol.find(
        id=key_universe_in_a_nutshell.replace(" ", "")
    )
    assert universe_citation is not None

    # Relativity theory it is referenced once
    universe_back_links = universe_citation.findAll("a")
    assert len(universe_back_links) == 1
