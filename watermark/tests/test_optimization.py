"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from pathlib import Path
from unittest.mock import patch

import tinify
from watermark.optimizer import optimize, validate_key
from watermark.watermark import add_watermark


def test_optimize(tmp_path, png):
    """Test the optimization."""
    image = tmp_path / "picture.png"
    png(image)

    watermarked = add_watermark(image, text="confidential")
    assert watermarked.is_file()

    class SourceMocked:
        @classmethod
        def from_file(cls, path):
            return cls()

        def to_file(self, path):
            Path(path).touch()

    def from_file(path):
        return SourceMocked.from_file(path)

    tinify.compression_count = 0

    with patch.object(tinify, "from_file", new=from_file):
        optimized = optimize(watermarked)

    assert optimized.is_file()

    # Already done
    assert optimize(optimized).name == optimized.name


def test_optimize_no_more_compression_counts(tmp_path, png):
    """Test zero compression count."""
    image = tmp_path / "picture.png"
    png(image)

    watermarked = add_watermark(image, text="confidential")
    assert watermarked.is_file()

    tinify.compression_count = 501
    assert optimize(watermarked) is None


def test_optimize_retry(tmp_path, png):
    """Test retries."""
    image = tmp_path / "picture.png"
    png(image)

    watermarked = add_watermark(image, text="confidential")
    assert watermarked.is_file()

    class SourceMocked:
        @classmethod
        def from_file(cls, path):
            raise tinify.ServerError("Mock'ed error")

    def from_file(path):
        return SourceMocked.from_file(path)

    tinify.compression_count = 1

    with patch.object(tinify, "from_file", new=from_file):
        assert optimize(watermarked) is None


def test_validate_key_empty():
    """Test empty key validation."""
    assert not validate_key("")


@patch("tinify.validate")
def test_validate_key_invalid(mocked_validate):
    """Test invalid key validation."""
    mocked_validate.side_effect = tinify.Error("Mock'ed error")
    assert not validate_key("invalid_key")


@patch("tinify.validate")
def test_validate_key_valid(mocked_validate):
    """Test valid key validation."""
    mocked_validate.return_value = True
    assert validate_key("valid_key")
