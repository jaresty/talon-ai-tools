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
