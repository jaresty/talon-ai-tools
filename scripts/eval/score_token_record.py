"""Score the '## Token application' record in a model reply.

Each line of the record is `<token>: "<quote>" - <what it did>`. The quote should
appear in the answer above the record. Matching tolerates formatting differences
(markdown, list numbers, table pipes, quote style, case, XML/HTML tags such as
SVG <text> elements) but not changed or dropped words.

Per-line status:
  verbatim   a quote is present and found in the answer
  not_found  a quote is present but is not in the answer
  unquoted   the line has no quoted text

Usage: python scripts/eval/score_token_record.py reply1.md reply2.md ...
"""
import re
import sys

_RECORD_HEADING = re.compile(r"^[#h\d. ]*token application\s*$", re.I | re.M)
_NEXT_HEADING = re.compile(r"^[#h\d. ]*model interpretation", re.I | re.M)
_LABEL = re.compile(r"\[?([A-Za-z0-9_\-]+)\]?\**\s*:")
_QUOTE = re.compile(r"[\"“](.{6,}?)[\"”]")


def _words(s):
    s = s.replace('\\"', '"').replace("\\n", " ")
    s = re.sub(r"<[^>]+>", " ", s)
    s = (
        s.replace("—", "-")
        .replace("–", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )
    s = re.sub(r"[*`_#|]", " ", s)
    s = re.sub(r"(?<!\w)\d+\.(?=\s)", " ", s)
    s = re.sub(r"[^\w\s']", " ", s)
    # Keep apostrophes inside words ("it's") but drop quote marks at word edges ('this').
    return [w for w in (w.strip("'") for w in s.lower().split()) if w]


def _contains(hay, needle):
    n = len(needle)
    if n == 0:
        return True
    return any(hay[i : i + n] == needle for i in range(len(hay) - n + 1))


def score_text(text):
    """Return [(token, status)] for the record in `text`, or None if there is no record."""
    m = _RECORD_HEADING.search(text)
    if not m:
        return None
    answer = _words(text[: m.start()])
    record = _NEXT_HEADING.split(text[m.end() :])[0]
    results = []
    for line in record.splitlines():
        line = line.strip().lstrip("-*• ").strip()
        label = _LABEL.match(re.sub(r"[*`_]", "", line))
        if not label:
            continue
        quote = _QUOTE.search(line)
        if not quote:
            results.append((label.group(1), "unquoted"))
            continue
        needle = _words(quote.group(1).split("...")[0])
        results.append((label.group(1), "verbatim" if _contains(answer, needle) else "not_found"))
    return results


def summarize(results):
    quoted = sum(1 for _, s in results if s != "unquoted")
    verbatim = sum(1 for _, s in results if s == "verbatim")
    return {"lines": len(results), "quoted": quoted, "verbatim": verbatim}


def main(argv):
    total = {"lines": 0, "quoted": 0, "verbatim": 0}
    for path in argv:
        with open(path, encoding="utf-8") as fh:
            results = score_text(fh.read())
        if results is None:
            print(f"{path}: NO RECORD")
            continue
        s = summarize(results)
        for k in total:
            total[k] += s[k]
        print(f"{path}: lines {s['lines']:2d} | quoted {s['quoted']:2d} | verbatim {s['verbatim']:2d}")
        for token, status in results:
            if status != "verbatim":
                print(f"    {token}: {status}")
    q, l = max(total["quoted"], 1), max(total["lines"], 1)
    print(
        f"TOTAL lines {total['lines']} | quoted {total['quoted']} ({100 * total['quoted'] // l}%) | "
        f"verbatim {total['verbatim']} = {100 * total['verbatim'] // q}% of quotes, {100 * total['verbatim'] // l}% of lines"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
