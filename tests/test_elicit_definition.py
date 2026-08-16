from lib.axisConfig import AXIS_KEY_TO_VALUE, AXIS_TOKEN_METADATA


def test_elicit_token_exists():
    assert "elicit" in AXIS_KEY_TO_VALUE["form"], "elicit token missing from form axis"


def test_elicit_definition_addresses_administrator():
    defn = AXIS_KEY_TO_VALUE["form"]["elicit"]
    assert "administering" in defn, "definition must reference the person administering"


def test_elicit_definition_holder_instructions():
    defn = AXIS_KEY_TO_VALUE["form"]["elicit"]
    assert "instruction to the holder" in defn, "definition must name instruction to the holder"


def test_elicit_distinction_vs_questions():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["elicit"]["distinctions"] if d["token"] == "questions"]
    assert notes, "questions distinction missing from elicit"
    assert "questions" in notes[0]


def test_elicit_distinction_vs_facilitate():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["elicit"]["distinctions"] if d["token"] == "facilitate"]
    assert notes, "facilitate distinction missing from elicit"
    assert "facilitate" in notes[0]


# property [1]: elicit no longer commits to a STATIC instrument (composes with a live loop)
def test_elicit_socratic_distinction_drops_static():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["elicit"]["distinctions"] if d["token"] == "socratic"]
    assert notes, "socratic distinction missing from elicit"
    assert "static" not in notes[0], (
        "elicit must not commit to a static instrument — it must compose with a live process"
    )


# property [2]: elicit heuristics no longer assert a SEPARATE administrator
def test_elicit_heuristics_drop_separate_administrator():
    heuristics = AXIS_TOKEN_METADATA["form"]["elicit"]["heuristics"]
    joined = " ".join(heuristics)
    assert "someone else" not in joined, (
        "elicit must not hard-code a separate administrator — the holder may be the responder itself"
    )


# property [3]: elicit still addresses the holder with ask/listen/record instructions
def test_elicit_definition_retains_ask_listen_record():
    defn = AXIS_KEY_TO_VALUE["form"]["elicit"]
    assert "instruction to the holder" in defn, "definition must name instruction to the holder"
    for verb in ("ask", "listen", "record"):
        assert verb in defn, f"elicit definition must retain the {verb!r} elicitation verb"


# property [4]: elicit keeps its distinctions from questions, socratic, and facilitate
def test_elicit_preserves_all_distinctions():
    tokens = {d["token"] for d in AXIS_TOKEN_METADATA["form"]["elicit"]["distinctions"]}
    for required in ("questions", "socratic", "facilitate"):
        assert required in tokens, f"elicit must preserve its distinction vs {required!r}"
