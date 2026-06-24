from lib.axisConfig import AXIS_KEY_TO_VALUE, AXIS_TOKEN_METADATA


def test_interactive_definition_v3_root():
    defn = AXIS_KEY_TO_VALUE["form"]["interactive"]
    assert "names at least one user-driven state transition" in defn


def test_interactive_definition_no_v2_root():
    defn = AXIS_KEY_TO_VALUE["form"]["interactive"]
    assert "presents at least one open element" not in defn


def test_interactive_cocreate_distinction_v3():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["interactive"]["distinctions"] if d["token"] == "cocreate"]
    assert notes, "cocreate distinction missing"
    assert "two distinct outcomes that depend on it" not in notes[0]


def test_interactive_socratic_distinction_v3():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["interactive"]["distinctions"] if d["token"] == "socratic"]
    assert notes, "socratic distinction missing"
    assert "determination point" not in notes[0]


# v4 tests — connectivity clause
def test_interactive_v4_connectivity():
    defn = AXIS_KEY_TO_VALUE["form"]["interactive"]
    assert "Where the response names more than one transition" in defn


def test_interactive_v4_no_outcome():
    defn = AXIS_KEY_TO_VALUE["form"]["interactive"]
    assert "state or outcome" not in defn


def test_interactive_cocreate_v4():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["interactive"]["distinctions"] if d["token"] == "cocreate"]
    assert notes, "cocreate distinction missing"
    assert "state or outcome" not in notes[0]


def test_interactive_socratic_v4():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["interactive"]["distinctions"] if d["token"] == "socratic"]
    assert notes, "socratic distinction missing"
    assert "state or outcome" not in notes[0]
