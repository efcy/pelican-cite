from typing import List, Match, Optional

import pytest

from .pelican_cite import CITE_RE


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
