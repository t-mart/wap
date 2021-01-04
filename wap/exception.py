class WAPException(Exception):
    """General WAP exception"""

    def __init__(self, message: str):
        self.message = message


class ConfigSemanticException(WAPException):
    """Indicates there was a problem with the data in the config"""


class ConfigSchemaException(WAPException):
    """Indicates the loaded yaml does not follow the yaml schema"""


class ConfigFileException(WAPException):
    """Indicates the config file could not be found"""


class DevInstallException(WAPException):
    """Indicates a problem during dev-installing"""


class WowAddonPathException(WAPException):
    """Indicates a wow addons path doesn't look right"""


class BuildException(WAPException):
    """Indicates a problem during building"""


class ReleaseException(WAPException):
    """Indicates a problem during releasing"""


class CurseForgeAPIException(WAPException):
    """Indicates a problem communicating with CurseForge"""
