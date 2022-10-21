from importlib.metadata import version

# this needs to match the package name that's installed, even if its binary is different
__name__ = "wow-addon-packager"
__version__ = version(__name__)
