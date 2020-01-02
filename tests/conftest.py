from logging import Logger
from unittest.mock import Mock

from pelican import ArticlesGenerator
from pelican_cite import ArticleCite, CiteHtml, Style
from pybtex.database import BibliographyData, Entry, Person
from pybtex.utils import OrderedCaseInsensitiveDict
import pytest


@pytest.fixture()
def get_global_bib_mock(
    mocker, entry_relativity_theory, entry_universe_in_a_nutshell
) -> Mock:
    mock = mocker.patch("pelican_cite._get_global_bib")

    entries = OrderedCaseInsensitiveDict(
        [
            (entry_relativity_theory.key, entry_relativity_theory),
            (entry_universe_in_a_nutshell.key, entry_universe_in_a_nutshell),
        ]
    )
    mock.return_value = BibliographyData(entries=entries)

    return mock


@pytest.fixture()
def logger_warning_mock(mocker) -> Mock:
    return mocker.patch.object(Logger, "warning")


@pytest.fixture()
def misc_cite_type():
    return "misc"


@pytest.fixture()
def book_cite_type():
    return "book"


@pytest.fixture()
def person_einstein():
    return Person(last="Einstein", first="Albert")


@pytest.fixture()
def person_hawking():
    return Person(last="Stephen", first="Hawking")


@pytest.fixture()
def key_relativity_theory():
    return "ein relt"


@pytest.fixture()
def key_universe_in_a_nutshell():
    return "hawuian"


@pytest.fixture()
def entry_relativity_theory(
    book_cite_type, person_einstein, key_relativity_theory
) -> Entry:
    entry = Entry(
        type_=book_cite_type,
        fields={
            "year": "2011",
            "title": "Relativity: The Special and General Theory",
            "publisher": "Emporum Books",
        },
        persons={"author": [person_einstein]},
    )
    entry.key = key_relativity_theory
    return entry


@pytest.fixture()
def entry_universe_in_a_nutshell(
    book_cite_type, person_hawking, key_universe_in_a_nutshell
):
    entry = Entry(
        type_=book_cite_type,
        fields={
            "year": "2001",
            "month": "november",
            "day": "6",
            "title": "The Universe in a Nutshell",
            "publisher": "Bantam",
        },
        persons={"author": [person_hawking]},
    )
    entry.key = key_universe_in_a_nutshell
    return entry


@pytest.fixture()
def style():
    return Style(label_style="alpha")


@pytest.fixture()
def cite_relativity_theory(key_relativity_theory, entry_relativity_theory, style):
    formatted_entries = style.format_entries([entry_relativity_theory])
    return ArticleCite(next(formatted_entries))


@pytest.fixture()
def cite_universe_in_a_nutshell(
    key_universe_in_a_nutshell, entry_universe_in_a_nutshell, style
):
    formatted_entries = style.format_entries([entry_universe_in_a_nutshell])
    return ArticleCite(next(formatted_entries))


@pytest.fixture()
def cite_html():
    return CiteHtml()


@pytest.fixture()
def articles_generator():
    context = {
        "BIBLIOGRAPHY_LABEL_STYLE": "alpha",
        "BIBLIOGRAPHY_NAME_STYLE": None,
        "BIBLIOGRAPHY_SORTING_STYLE": "author_year_title",
    }
    return ArticlesGenerator(
        context=context,
        settings={
            "ARTICLES_ON_HOMEPAGE": 5,
            "ARTICLE_EXCLUDES": ["pages"],
            "ARTICLE_LANG_SAVE_AS": "{slug}-{lang}.html",
            "ARTICLE_LANG_URL": "{slug}-{lang}.html",
            "ARTICLE_ORDER_BY": "reversed-date",
            "ARTICLE_PATHS": [""],
            "ARTICLE_PERMALINK_STRUCTURE": "",
            "ARTICLE_SAVE_AS": "articles/{category}/{slug}/index.html",
            "ARTICLE_TRANSLATION_ID": "slug",
            "ARTICLE_URL": "articles/{category}/{slug}/",
            "AUTHOR": "",
            "AUTHOR_FEED_ATOM": None,
            "AUTHOR_FEED_RSS": None,
            "AUTHOR_SAVE_AS": "author/{slug}/index.html",
            "AUTHOR_URL": "author/{slug}/",
            "BIND": "127.0.0.1",
            "CACHE_CONTENT": False,
            "CACHE_PATH": "cache",
            "CATEGORY_FEED_ATOM": None,
            "CATEGORY_SAVE_AS": "category/{slug}/index.html",
            "CATEGORY_URL": "category/{slug}/",
            "CHECK_MODIFIED_METHOD": "mtime",
            "CONTENT_CACHING_LAYER": "reader",
            "CSS_FILE": "main.css",
            "DATE_FORMATS": {},
            "DAY_ARCHIVE_SAVE_AS": "",
            "DAY_ARCHIVE_URL": "",
            "DEBUG": False,
            "DEFAULT_CATEGORY": "misc",
            "DEFAULT_DATE_FORMAT": "%a %d %B %Y",
            "DEFAULT_LANG": "en",
            "DEFAULT_METADATA": {},
            "DEFAULT_ORPHANS": 0,
            "DEFAULT_PAGINATION": False,
            "DELETE_OUTPUT_DIRECTORY": False,
            "DIRECT_TEMPLATES": [],
            "DISPLAY_CATEGORIES_ON_MENU": True,
            "DISPLAY_PAGES_ON_MENU": True,
            "DOCUTILS_SETTINGS": {},
            "DRAFT_LANG_SAVE_AS": "drafts/{slug}-{lang}.html",
            "DRAFT_LANG_URL": "drafts/{slug}-{lang}.html",
            "DRAFT_PAGE_LANG_SAVE_AS": "drafts/pages/{slug}-{lang}.html",
            "DRAFT_PAGE_LANG_URL": "drafts/pages/{slug}-{lang}.html",
            "DRAFT_PAGE_SAVE_AS": "drafts/pages/{slug}.html",
            "DRAFT_PAGE_URL": "drafts/pages/{slug}.html",
            "DRAFT_SAVE_AS": "drafts/{slug}/index.html",
            "DRAFT_URL": "drafts/{slug}",
            "EXTRA_PATH_METADATA": {},
            "FAVICON": "/img/favicon-32.png",
            "FEED_ALL_ATOM": None,
            "FEED_DOMAIN": "",
            "FEED_MAX_ITEMS": "",
            "FILENAME_METADATA": "(?P<date>\\d{4}-\\d{2}-\\d{2}).*",
            "FORMATTED_FIELDS": ["summary"],
            "GZIP_CACHE": True,
            "IGNORE_FILES": [".#*"],
            "INDEX_SAVE_AS": "index.html",
            "INTRASITE_LINK_REGEX": "[{|](?P<what>.*?)[|}]",
            "JINJA_ENVIRONMENT": {
                "extensions": ["jinja2.ext.loopcontrols"],
                "lstrip_blocks": True,
                "trim_blocks": True,
            },
            "JINJA_FILTERS": {},
            "LOAD_CONTENT_CACHE": False,
            "LOCALE": [""],
            "LOG_FILTER": [],
            "MARKDOWN": {},
            "MONTH_ARCHIVE_SAVE_AS": "articles/{date:%Y}/{date:%b}/index.html",
            "MONTH_ARCHIVE_URL": "articles/{date:%Y}/{date:%b}/",
            "NEWEST_FIRST_ARCHIVES": True,
            "OUTPUT_PATH": "output",
            "OUTPUT_RETENTION": [],
            "OUTPUT_SOURCES": False,
            "OUTPUT_SOURCES_EXTENSION": ".text",
            "PAGE_EXCLUDES": [""],
            "PAGE_LANG_SAVE_AS": "pages/{slug}-{lang}.html",
            "PAGE_LANG_URL": "pages/{slug}-{lang}.html",
            "PAGE_ORDER_BY": "basename",
            "PAGE_PATHS": ["pages"],
            "PAGE_SAVE_AS": "pages/{slug}/index.html",
            "PAGE_TRANSLATION_ID": "slug",
            "PAGE_URL": "pages/{slug}/",
            "PAGINATED_TEMPLATES": {
                "author": 10,
                "category": 10,
                "index": None,
                "tag": 1,
            },
            "PAGINATION_PATTERNS": [],
            "PATH": "/Users/johanvergeer/workspace/redgyro-blog/content",
            "PATH_METADATA": "",
            "PELICAN_CLASS": "pelican.Pelican",
            "PLUGINS": [],
            "PLUGIN_PATHS": [],
            "PORT": 8000,
            "PUBLICATIONS_SRC": "content/pubs.bib",
            "PYGMENTS_RST_OPTIONS": {},
            "READERS": {},
            "READ_MORE": "Read more",
            "RELATIVE_URLS": False,
            "REVERSE_CATEGORY_ORDER": False,
            "RSS_FEED_SUMMARY_ONLY": True,
            "SITENAME": "",
            "SITEURL": "",
            "SLUGIFY_SOURCE": "title",
            "SLUG_REGEX_SUBSTITUTIONS": [],
            "SOCIAL": (),
            "STATIC_CHECK_IF_MODIFIED": False,
            "STATIC_CREATE_LINKS": False,
            "STATIC_EXCLUDES": [],
            "STATIC_EXCLUDE_SOURCES": True,
            "STATIC_PATHS": ["img"],
            "STATIC_SAVE_AS": "{path}",
            "STATIC_URL": "{path}",
            "SUMMARY_MAX_LENGTH": 50,
            "TAG_SAVE_AS": "tag/{slug}/index.html",
            "TAG_URL": "tag/{slug}/",
            "TEMPLATE_EXTENSIONS": [".html"],
            "TEMPLATE_PAGES": {},
            "THEME": "",
            "THEME_STATIC_DIR": "theme",
            "THEME_STATIC_PATHS": ["static"],
            "THEME_TEMPLATES_OVERRIDES": [],
            "TIMEZONE": "Europe/Amsterdam",
            "TRANSLATION_FEED_ATOM": None,
            "TYPOGRIFY": False,
            "TYPOGRIFY_IGNORE_TAGS": [],
            "USE_FOLDER_AS_CATEGORY": True,
            "WITH_FUTURE_DATES": True,
            "WRITE_SELECTED": [],
            "YEAR_ARCHIVE_SAVE_AS": "articles/{date:%Y}/index.html",
            "YEAR_ARCHIVE_URL": "articles/{date:%Y}/",
        },
        path="",
        theme="",
        output_path="",
    )
