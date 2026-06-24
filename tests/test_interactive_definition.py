from lib.axisConfig import AXIS_KEY_TO_VALUE, AXIS_TOKEN_METADATA


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


# v5 tests — present-state + withheld-output framing
def test_interactive_v5_clause1():
    defn = AXIS_KEY_TO_VALUE["form"]["interactive"]
    assert "names a current state and at least one available input from that state" in defn


def test_interactive_v5_clause2():
    defn = AXIS_KEY_TO_VALUE["form"]["interactive"]
    assert "ends with a prompt that itself names at least one of those inputs" in defn



def test_interactive_v5_no_v4_root():
    defn = AXIS_KEY_TO_VALUE["form"]["interactive"]
    assert "names at least one user-driven state transition" not in defn


def test_interactive_cocreate_v5():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["interactive"]["distinctions"] if d["token"] == "cocreate"]
    assert notes, "cocreate distinction missing"
    assert "user-driven state transition" not in notes[0]


def test_interactive_socratic_v5():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["interactive"]["distinctions"] if d["token"] == "socratic"]
    assert notes, "socratic distinction missing"
    assert "user-driven state transition" not in notes[0]


# v6 tests — causal-claim framing replaces information-hiding framing
def test_interactive_v6_clause4():
    defn = AXIS_KEY_TO_VALUE["form"]["interactive"]
    assert "does not assert that any named input produces a named system state" in defn


def test_interactive_v6_causal_form():
    defn = AXIS_KEY_TO_VALUE["form"]["interactive"]
    assert "causal claims" in defn and "withheld until the user acts" in defn


def test_interactive_v6_no_v5_clause4():
    defn = AXIS_KEY_TO_VALUE["form"]["interactive"]
    assert "does not name by name the system state any input produces" not in defn


def test_interactive_v6_cocreate():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["interactive"]["distinctions"] if d["token"] == "cocreate"]
    assert notes, "cocreate distinction missing"
    assert "causal claims" in notes[0] or "withholds" in notes[0]


def test_interactive_v6_socratic():
    notes = [d["note"] for d in AXIS_TOKEN_METADATA["form"]["interactive"]["distinctions"] if d["token"] == "socratic"]
    assert notes, "socratic distinction missing"
    assert "causal claims" in notes[0] or "withholds" in notes[0]
