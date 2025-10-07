import builtins
from unittest.mock import patch

import src.util.log as log


def test_msg():
    with patch.object(builtins, "print") as mock_print:
        log.msg("Test")
        mock_print.assert_called_with("• Test")
        log.msg("Test", "!")
        mock_print.assert_called_with("! Test")


def test_info():
    with patch.object(builtins, "print") as mock_print:
        log.info("Downloading …")
        mock_print.assert_called_with("\x1b[36m  →\x1b[0m Downloading …")
        log.info("Done", " ✓", prefix="")
        mock_print.assert_called_with("Done\x1b[90m ✓\x1b[0m")


def test_success():
    with patch.object(builtins, "print") as mock_print:
        log.success("Fetched 14 files")
        mock_print.assert_called_with("\x1b[32m✓\x1b[0m Fetched 14 files")
        log.success("Done", " 🎉", prefix="¡")
        mock_print.assert_called_with("\x1b[32m¡\x1b[0m Done\x1b[90m 🎉\x1b[0m")


def test_error():
    with patch.object(builtins, "print") as mock_print:
        log.error("Oh, no!")
        mock_print.assert_called_with("\x1b[31m  ✗\x1b[0m Oh, no!")
        log.error("Aaaargh", " 😱", prefix="💥")
        mock_print.assert_called_with("\x1b[31m💥\x1b[0m Aaaargh\x1b[90m 😱\x1b[0m")
