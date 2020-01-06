"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
from watermark.watermark import add_watermark, apply_watermarks
from watermark.utils import guess_output


def test_watermark_both(tmp_path, picture, png):
    """Test both text and picture watermarks."""
    image = tmp_path / "text-and-picture.png"
    png(image)

    text = "www.arresto-momentum.com"
    img = add_watermark(image, text=text, picture=picture)
    assert img is not None

    output = image.with_name("text-and-picture-w.jpg")
    assert output.is_file()

    # Calling twice should return the already processed file
    assert add_watermark(image, text=text, picture=picture)


def test_watermark_picture(tmp_path, picture, png):
    """Test a picture watermark."""
    image = tmp_path / "picture-only.png"
    png(image)

    add_watermark(image, picture=picture)

    output = image.with_name("picture-only-w.jpg")
    assert output.is_file()


def test_watermark_text(tmp_path, png):
    """Test a text watermark."""
    image = tmp_path / "text-only.png"
    png(image)

    add_watermark(image, text="www.arresto-momentum.com")

    output = image.with_name("text-only-w.jpg")
    assert output.is_file()


def test_apply_watermark(tmp_path, location, picture, png):
    """Test apply watermarks to several files.

    Create the following tree:

        - text-and-picture-{0..9}.png
        - folder
            - sub-folder
                - text-and-picture-10.png
            - 東京スカイツリー.png
            - Наксео Драйв.png
            - Pôm p¤m G@llÿ' ¤.png
    """

    # Create the tree
    root = tmp_path
    folder = root / "folder"
    subfolder = folder / "sub-folder"
    subfolder.mkdir(parents=True)

    # Create files
    png(folder / "東京スカイツリー.png"),
    png(folder / "Наксео Драйв.png"),
    png(folder / "Pôm p¤m G@llÿ' ¤.png"),
    png(subfolder / "text-and-picture-10.png"),

    paths = [png(root / f"text-and-picture-{n}.png") for n in range(10)]
    paths.append(folder)

    text = "www.arresto-momentum.com"
    list(apply_watermarks(paths, text=text, picture=picture))

    for file in root.glob("**/*.png"):
        assert guess_output(file).is_file()


def test_file_not_an_image(location):
    """Test a file that is not an image."""
    img = add_watermark(location.parent / "conftest.py", text="foo")
    assert img is None


def test_file_not_found(location):
    """Test a file that does not exist."""
    img = add_watermark(location.parent / "inexistant.png", text="foo")
    assert img is None
