"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
import logging
from pathlib import Path
from typing import Any, List

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from .conf import CONF


def add_watermark(image: Path, text: str = "", picture: str = "") -> Image:
    """Add a given picture *watermark* and/or a given *text* to a given *image*
    using the specified *opacity*.
    Source: https://gist.github.com/makmac213/a4ab09f5a042c5477037
    """
    # A new file will be created with the "-w" letters appended to the original name
    # ("w" for "watermarked")
    output = image.with_name(f"{image.stem}-w.jpg")

    # We should not erase old work, stop here.
    if output.is_file():
        logging.info(f"{image} already processed")
        return None

    try:
        with image.open("rb") as finput:
            img = Image.open(finput).convert("RGB")
    except OSError:
        logging.warning(f"Skipping unprocessable {image}")
        return None

    if text:
        logging.info(f"Applying text watermark {text!r} on {image}")
        img = add_text_watermark(img, text)
    if picture:
        logging.info(f"Applying picture watermark {picture!r} on {image}")
        img = add_picture_watermark(img, picture)

    img.save(output, "JPEG")
    return img


def add_picture_watermark(img: Image, watermark: str) -> Image:
    """Add a given picture *watermark* to a given *img* using the specified *opacity*.
    Source: https://gist.github.com/makmac213/a4ab09f5a042c5477037
    """
    watermark_img = Image.open(watermark)

    """
    # Resize to 25% of real dimensions
    w = int(watermark_img.size[0] * 0.25)
    h = int(watermark_img.size[1] * 0.25)
    watermark_img = watermark_img.resize((w, h), Image.ANTIALIAS)
    """

    if CONF.opacity:
        alpha = watermark_img.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(CONF.opacity)
        watermark_img.putalpha(alpha)

    # Center
    position = (
        int((img.size[0] - watermark_img.size[0]) / 2),
        int((img.size[1] - watermark_img.size[1]) / 2),
    )

    final = Image.new("RGBA", img.size, (0, 0, 0, 0))
    final.paste(img, (0, 0))
    final.paste(watermark_img, position, mask=watermark_img)

    return Image.composite(final, img, final)


def add_text_watermark(img: Image, watermark: str) -> Image:
    """Add a given text *watermark* to a given *img* using the specified *opacity* and *font*.
    *font* is the full path to the TrueType file.
    Source: http://www.pythoncentral.io/watermark-images-python-2x/
    """
    watermark_img = Image.new("RGBA", img.size, (0, 0, 0, 0))

    size = 2
    n_font = ImageFont.truetype(CONF.font, size)
    n_width, n_height = n_font.getsize(watermark)

    while n_width + n_height < watermark_img.size[0]:
        size += 2
        n_font = ImageFont.truetype(CONF.font, size)
        n_width, n_height = n_font.getsize(watermark)

    draw = ImageDraw.Draw(watermark_img, "RGBA")
    draw.text(
        ((watermark_img.size[0] - n_width) / 2, (watermark_img.size[1] - n_height) / 2),
        # ((watermark_img.size[0] - n_width) / 2, 10),
        watermark,
        font=n_font,
    )

    alpha = watermark_img.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(CONF.opacity)
    watermark_img.putalpha(alpha)

    return Image.composite(watermark_img, img, watermark_img)


def apply_watermarks(paths: List[Path], text: str, picture: str, **kwargs: Any) -> None:
    """Apply watermark(s) on given files."""
    for path in paths:
        if path.is_file():
            add_watermark(path, text=text, picture=picture)
        elif path.is_dir():
            for filters in CONF.extensions:
                apply_watermarks(list(path.glob(filters)), text=text, picture=picture)
