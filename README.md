# Watermark GUI

[![Build Status](https://travis-ci.org/BoboTiG/watermark-me.svg?branch=master)](https://travis-ci.org/BoboTiG/watermark-me)

GUI to watermark your pictures with text and/or another picture.
Code name: Colossos.

Installation:

```bash
python3 -m pip install watermark
```

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

## Credits

Icon made by srip from [www.flaticon.com](https://www.flaticon.com/free-icon/optimize_2344561).

Tests data (logo and font) are used with the blessing of the creator of [Arresto Momentum](https://www.arresto-momentum.com/).
