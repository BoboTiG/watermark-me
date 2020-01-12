"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.

Source: https://github.com/nuxeo/nuxeo-drive/blob/master/nxdrive/translator.py
"""
import json
import re
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .conf import CONF
from .constants import DATA_DIR


class Translator:
    def __init__(self, path: Path, lang: str = "") -> None:
        self.locale = ""
        self._labels: Dict[str, Dict[str, str]] = {}

        # Load from JSON
        for translation in path.iterdir():
            label = translation.stem
            self._labels[label] = json.loads(translation.read_text(encoding="utf-8"))

        # List language
        self.langs: Dict[str, Tuple[str, str]] = {}
        for key in self._labels:
            self.langs[key] = (key, self._labels[key]["LANGUAGE"])

        # Select one
        try:
            self.set(lang)
        except ValueError:
            self.set("en")
        self._fallback = self._labels["en"]

    @staticmethod
    def _tokenize(label: str, values: List[Any] = None) -> str:
        """
        Format the label with its arguments.

        Qt strings differ from Python ones in two ways:
        - They use "%x" instead of "{x}" to add arguments through formatting,
        so we use a regex to substitute them.
        - Their arguments indexes start at 1 instead of 0, so we pass the
        values with an empty entry at the beginning.
        """
        if not values:
            return label

        result = re.sub(r"%(\d+)", r"{\1}", label)
        return result.format(*([""] + values))

    def get(self, label: str, values: List[Any] = None) -> str:
        with suppress(KeyError):
            return self._tokenize(self._current[label], values)

        with suppress(KeyError):
            return self._tokenize(self._fallback[label], values)

        return label

    def set(self, lang: str) -> None:
        try:
            self._current = self._labels[lang]
        except KeyError:
            raise ValueError(f"Unknown language {lang!r}")
        else:
            if self.locale != lang:
                self.locale = lang


TR = Translator(DATA_DIR / "i18n", lang=CONF.lang)
