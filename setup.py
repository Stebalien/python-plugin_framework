from distutils.core import setup
from plugin_framework import __version__, __doc__, __author__, __email__


setup(
    name = "plugin_framework",
    version = __version__,
    description = "A simpole plugin loading framework.",
    long_description = __doc__,
    author = __author__,
    author_email = __email__,
    py_modules = ['plugin_framework'],
    url = 'https://github.com/stebalien/plugin_framework',
)


