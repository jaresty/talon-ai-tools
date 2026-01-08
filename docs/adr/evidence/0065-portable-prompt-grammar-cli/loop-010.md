## loop-010 red | helper:rerun git show HEAD:_tests/test_readme_portable_cli.py
- timestamp: 2026-01-08T03:58:17Z
- exit status: 128
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  fatal: path '_tests/test_readme_portable_cli.py' exists on disk, but not in 'HEAD'
  ```

## loop-010 green | helper:rerun python3 -m unittest _tests.test_readme_portable_cli
- timestamp: 2026-01-08T03:57:24Z
- exit status: 0
- helper:diff-snapshot=3 files changed, 51 insertions(+)
- excerpt:
  ```
  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.000s

  OK
  ```
