# setup.py
"""
Build with:
    python setup.py py2app
"""

from setuptools import setup

APP = ["run_app.py"]  # or whatever your main script is
OPTIONS = {
    "argv_emulation": True,
    "site_packages": True,  # so py2app bundles site-packages
    "plist": {
        "PyRuntimeLocations": [
            # This matches the version from your otool -L.
            # We'll use 3.11 in the path. If you change Python versions, update this.
            "/Users/danielpowell/.pyenv/versions/3.11.6/Library/Frameworks/Python.framework/Versions/3.11/Python",

            # A second fallback can be "Current" if you like
            "/Users/danielpowell/.pyenv/versions/3.11.6/Library/Frameworks/Python.framework/Versions/3.11/Python",
        ],
    },
}

setup(
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
