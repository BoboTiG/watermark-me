"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
import pytest

from watermark.constants import DATA_DIR
from watermark.translator import TR, Translator


def test_load_file():
    # Verify the call to save
    TR.set("en")
    assert TR.locale == "en"

    # Change to an existing language
    TR.set("fr")
    assert TR.locale == "fr"

    # Test unkown key
    assert TR.get("BOUZOUF") == "BOUZOUF"

    # Try to switch to bad language
    with pytest.raises(ValueError):
        TR.set("abcd")
    assert TR.locale == "fr"

    # Go back to an existing one
    TR.set("en")
    assert TR.locale == "en"
    assert TR.get("BOUZOUF") == "BOUZOUF"


def test_bad_lang():
    Translator.singleton = None
    Translator(DATA_DIR / "i18n", lang="unk")


def test_translate_twice(location):
    """ Check that the values array is not mutated. """
    values = ["value"]
    first = TR.get("TITLE_SETTINGS", values)
    second = TR.get("TITLE_SETTINGS", values)

    assert first == second
    assert values == ["value"]


def test_no_value():
    assert "%1" in TR.get("TITLE_SETTINGS", [])


def test_languages():
    assert TR.langs == {"en": ("en", "English"), "fr": ("fr", "Français")}
