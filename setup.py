import setuptools

md = {
    "name": "dasm",
    "version": "1.0.0",
    "author": "HugeBrain16",
    "url": "https://github.com/HugeBrain16/dasm",
    "license": "MIT",
    "description": "WAYTOODANK assembly discord bot",
    "install_requires": ["cmdtools-py", "discord.py"],
    "packages": ["dasm", ],
    "long_description": open("README.md", "r", encoding="UTF8").read(),
    "long_description_content_type": "text/markdown",
}

setuptools.setup(**md)
