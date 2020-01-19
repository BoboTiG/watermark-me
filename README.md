# Watermark GUI

[![Build Status](https://travis-ci.org/BoboTiG/watermark-me.svg?branch=master)](https://travis-ci.org/BoboTiG/watermark-me)

GUI to watermark your pictures with text and/or another picture.
Code name: Colossos.

![Watermark-me! main window][watermark-me-preview]

[watermark-me-preview]: https://raw.githubusercontent.com/BoboTiG/watermark-me/master/preview.png

Installation:

```bash
python3 -m pip install watermark
```

To enable JPG optimizations, you will need a [Tinify API key](https://Tinify.com/developers) (free).

## Hacking

```bash
# Setup the virtualenv
python3 -m venv ~/venv3
. ~/venv3/bin/activate

# Setup pre-commit for automatic code quality checks before commit
python -m pip install -U --user pre-commit
pre-commit install
```

## Testing

```bash
python -m pip install -U --user tox
tox
```

Tested OK on:
- GNU/Linux Debian 10 (buster)
- macOS 10.14.6 (Mojave)
- Microsoft Windows 10

## Installers

### Windows

Double-click on `build-win.bat` (think to update environment variables first).


## Credits

Icon made by srip from [www.flaticon.com](https://www.flaticon.com/free-icon/optimize_2344561).

Tests data (logo and font) are used with the blessing of the creator of [Arresto Momentum](https://www.arresto-momentum.com/).

Windows installer final wizard picture taken from https://www.reddit.com/r/wallpapers/comments/cpkvnl/retro_style_wallpaper_2560x1440/.
