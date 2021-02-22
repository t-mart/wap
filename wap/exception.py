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


class WoWVersionException(WAPException):
    """Indicates a problem creating a version"""


class DevInstallException(WAPException):
    """Indicates a problem during dev-installing"""


class BuildException(WAPException):
    """Indicates a problem during building"""


class TocException(WAPException):
    """Indicates a problem with a TOC file"""


class UploadException(WAPException):
    """Indicates a problem during uploading"""


class CurseForgeAPIException(WAPException):
    """Indicates a problem communicating with CurseForge"""


class QuickstartException(WAPException):
    """Indicates a creating a new project"""


class NewConfigException(WAPException):
    """Indicates a creating a new configuration file"""
