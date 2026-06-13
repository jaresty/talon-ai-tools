import re


def _get_vet_definition():
    with open("lib/axisConfig.py") as f:
        content = f.read()
    # Collect all string fragments after "vet": (handles implicit concatenation).
    match = re.search(r'"vet":\s*((?:"[^"]*"\s*)+),', content)
    assert match, "vet definition not found in lib/axisConfig.py"
    fragments = re.findall(r'"([^"]*)"', match.group(1))
    return "".join(fragments)


def test_vet_definition_contains_transcript_showed():
    defn = _get_vet_definition()
    assert "what the transcript showed" in defn


def test_vet_definition_contains_null_results_as_gaps():
    defn = _get_vet_definition()
    assert "naming null results as gaps, not as disconfirmation" in defn


def test_vet_definition_contains_not_from_what_was_absent():
    defn = _get_vet_definition()
    assert "not from what was absent" in defn


def test_vet_definition_contains_prior_prediction():
    defn = _get_vet_definition()
    assert "prior prediction" in defn
