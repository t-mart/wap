class WapError(Exception):
    """General WAP exception"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AbortError(WapError):
    """Indicates the user aborted the operation."""


class ConfigError(WapError):
    """Indicates a general problem with the config."""


class ConfigPathError(WapError):
    """Indicates a problem accessing a configuration value"""


class ConfigValueError(WapError):
    """Indicates a problem encoding a configuration value to JSON"""


class ConfigSchemaError(WapError):
    """Indicates a config does not follow the schema."""


class CurseForgeAPIError(WapError):
    """Indicates a problem communicating with CurseForge"""


class EncodingError(WapError):
    """Indicates an issue encoding or decoding data"""


class PathExistsError(WapError):
    """Indicates a path exists that should not"""


class PathMissingError(WapError):
    """Indicates a needed path does not exist."""


class PathTypeError(WapError):
    """Indicates a path is not of the type expected (directory, file, etc)."""


class PlatformError(WapError):
    """Indicates that the current platform does not have a required feature."""


class TagError(WapError):
    """Indicates a malformed tag inside a TOC."""


class VersionError(WapError):
    """Indicates that a version is invalid when parsed."""
