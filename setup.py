import setuptools
from dasm import __version__ as version

md = {
    "name": "dasm",
    "version": version,
    "author": "HugeBrain16",
    "url": "https://github.com/HugeBrain16/dasm",
    "license": "MIT",
    "description": "WAYTOODANK assembly discord bot",
    "requires": ["cmdtools-py", "discord.py"],
    "packages": ["dasm", ],
    "long_description": open("README.md", "r", encoding="UTF8").read(),
    "long_description_content_type": "text/markdown",
}

setuptools.setup(**md)
