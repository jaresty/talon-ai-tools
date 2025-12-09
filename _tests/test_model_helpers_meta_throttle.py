import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelHelpers
    from talon_user.lib.modelState import GPTState

    class StreamStateMetaThrottleTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.last_meta = ""
            GPTState.text_to_confirm = ""

        def test_meta_updates_throttled(self) -> None:
            last_meta_update_ms = [0]
            meta_prefix = "## Model interpretation"
            base_answer = "body text"

            with patch.object(modelHelpers.time, "time", return_value=1.0):
                modelHelpers._update_stream_state_from_text(
                    f"{base_answer}\n{meta_prefix}\nfirst",
                    meta_throttle_ms=250,
                    last_meta_update_ms=last_meta_update_ms,
                )
            self.assertEqual(GPTState.last_meta, f"{meta_prefix}\nfirst")

            with patch.object(modelHelpers.time, "time", return_value=1.1):
                modelHelpers._update_stream_state_from_text(
                    f"{base_answer}\n{meta_prefix}\nsecond",
                    meta_throttle_ms=250,
                    last_meta_update_ms=last_meta_update_ms,
                )
            # Within the throttle window, meta should not update.
            self.assertEqual(GPTState.last_meta, f"{meta_prefix}\nfirst")

            with patch.object(modelHelpers.time, "time", return_value=1.4):
                modelHelpers._update_stream_state_from_text(
                    f"{base_answer}\n{meta_prefix}\nthird",
                    meta_throttle_ms=250,
                    last_meta_update_ms=last_meta_update_ms,
                )
            self.assertEqual(GPTState.last_meta, f"{meta_prefix}\nthird")
else:
    class StreamStateMetaThrottleTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass
