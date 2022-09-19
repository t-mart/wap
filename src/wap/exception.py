class WapException(Exception):
    """General WAP exception"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ConfigException(WapException):
    """Indicates a general problem with the config."""


class ConfigPathException(WapException):
    """Indicates a problem accessing a configuration value"""


class ConfigValueException(WapException):
    """Indicates a problem encoding a configuration value to JSON"""


class ConfigSchemaException(WapException):
    """Indicates a config does not follow the schema."""


class CurseForgeAPIException(WapException):
    """Indicates a problem communicating with CurseForge"""


class EncodingException(WapException):
    """Indicates an issue encoding or decoding data"""


class PathExistsException(WapException):
    """Indicates a path exists that should not"""


class PathMissingException(WapException):
    """Indicates a needed path does not exist."""


class PathTypeException(WapException):
    """Indicates a path is not of the type expected (directory, file, etc)."""


class PlatformException(WapException):
    """Indicates that the current platform does not have a required feature."""
