"""Tests for scripts/eval/score_token_record.py.

The scorer checks that each quote in a reply's '## Token application' record
appears in the answer above it, tolerating formatting differences (markdown,
list numbers, table pipes, quote style, case, XML tags) but not changed words.
"""
import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "scripts" / "eval" / "score_token_record.py"
_spec = importlib.util.spec_from_file_location("score_token_record", _PATH)
scorer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scorer)


def _reply(answer: str, record: str) -> str:
    return f"{answer}\n\n## Token application\n\n{record}\n\n## Model interpretation\n\nnotes\n"


def _status(text: str) -> dict:
    return dict(scorer.score_text(text))


def test_exact_quote_is_verbatim():
    t = _reply("The batch runs late because inputs arrive late.", '- full: "The batch runs late because inputs arrive late." - covers it')
    assert _status(t) == {"full": "verbatim"}


def test_changed_words_are_not_found():
    t = _reply("The batch runs late because inputs arrive late.", '- full: "The batch runs late because inputs show up late." - covers it')
    assert _status(t) == {"full": "not_found"}


def test_formatting_differences_are_tolerated():
    answer = "1. **Scope creeps** because no one said \"this is final\".\n| Attractors | Repellers |"
    record = (
        '- audit: "Scope creeps because no one said \'this is final\'." - x\n'
        '- polar: "Attractors | Repellers" - y'
    )
    assert _status(_reply(answer, record)) == {"audit": "verbatim", "polar": "verbatim"}


def test_case_and_curly_quotes_are_tolerated():
    t = _reply("It’s the Dependency map that matters.", '- depends: "it\'s the dependency map that matters" - x')
    assert _status(t) == {"depends": "verbatim"}


def test_text_split_across_xml_tags_still_matches():
    answer = '<text x="1">If actual is over</text><text x="2">by 30%: estimation error</text>'
    t = _reply(answer, '- rigor: "If actual is over by 30%: estimation error" - x')
    assert _status(t) == {"rigor": "verbatim"}


def test_a_line_with_no_quote_is_unquoted():
    t = _reply("Some answer text here.", "- jog: Keeps the framing balanced throughout the response.")
    assert _status(t) == {"jog": "unquoted"}


def test_bracket_and_bold_labels_are_recognised():
    t = _reply("alpha beta gamma delta", '- **mean**: "alpha beta gamma" - x\n- [form]: "beta gamma delta" - y')
    assert _status(t) == {"mean": "verbatim", "form": "verbatim"}


def test_no_record_returns_none():
    assert scorer.score_text("Just an answer with no record section.") is None


def test_quotes_in_the_record_do_not_count_as_the_answer():
    t = _reply("Short answer.", '- full: "text only present in the record itself" - x')
    assert _status(t) == {"full": "not_found"}


def test_summary_counts():
    results = [("a", "verbatim"), ("b", "not_found"), ("c", "unquoted"), ("d", "verbatim")]
    s = scorer.summarize(results)
    assert s == {"lines": 4, "quoted": 3, "verbatim": 2}
