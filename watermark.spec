# -*- mode: python -*-
# coding: utf-8

import io
import os
import os.path
import re
import sys

from PyInstaller.utils.hooks import copy_metadata

def get_version(init_file):
    """ Find the current version. """

    with io.open(init_file, encoding="utf-8") as handler:
        for line in handler.readlines():
            if line.startswith("__version__"):
                return re.findall(r"\"(.+)\"", line)[0]


app_name = os.environ["REPOSITORY_NAME"]
cwd = os.getcwd()
packaging = os.path.join(cwd, "packaging")
sources = os.path.join(cwd, app_name)
icon = {
    "win32": os.path.join(packaging, "windows", "pictures", "app_icon.ico"),
}[sys.platform]

excludes = [
    # https://github.com/pyinstaller/pyinstaller/wiki/Recipe-remove-tkinter-tcl
    "FixTk",
    "tcl",
    "tk",
    "_tkinter",
    "tkinter",
    "Tkinter",
    # Misc
    "ipdb",
    "lib2to3",
    "numpy",
    "pydev",
    "scipy",
    "yappi",
]

data = [(os.path.join(sources, "data"), "data"), (os.path.join(sources, "res"), "res")]
data.extend(copy_metadata("tendo"))  # See issue #75
version = get_version(os.path.join(sources, "__init__.py"))
properties_rc = None

if sys.platform == "win32":
    # Set executable properties
    properties_tpl = packaging + "\\windows\\properties_tpl.rc"
    properties_rc = packaging + "\\windows\\properties.rc"
    if os.path.isfile(properties_rc):
        os.remove(properties_rc)

    # Remove beta notation
    version = version.split("b")[0]
    version_tuple = tuple(map(int, version.split(".") + [0] * (3 - version.count("."))))

    with open(properties_tpl) as tpl, open(properties_rc, "w") as out:
        content = tpl.read().format(version=version, version_tuple=version_tuple)
        print(content)
        out.write(content)

a = Analysis(
    [os.path.join(sources, "__main__.py")],
    datas=data,
    excludes=excludes,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name=app_name,
    console=False,
    debug=False,
    strip=False,
    upx=False,
    icon=icon,
    version=properties_rc,
)

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name=app_name)
