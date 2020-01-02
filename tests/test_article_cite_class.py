def test_rendered_label(cite_relativity_theory):
    assert cite_relativity_theory.rendered_label == "Ein11"


def test_rendered_entry(cite_relativity_theory):
    assert (
        cite_relativity_theory.rendered_entry
        == "Albert Einstein.\n<em>Relativity: The Special and General Theory</em>.\nEmporum Books, 2011."
    )


def test_ref_id(cite_relativity_theory, key_relativity_theory):
    assert cite_relativity_theory.ref_id == key_relativity_theory.replace(" ", "")


def test_cite_key(cite_relativity_theory, key_relativity_theory):
    assert cite_relativity_theory.cite_key == key_relativity_theory
