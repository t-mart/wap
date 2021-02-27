from __future__ import annotations

from pathlib import Path

import attr

from wap import log

CHANGELOG_SUFFIX_MAP = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".txt": "text",
}

CHANGELOG_TYPES = {t for t in CHANGELOG_SUFFIX_MAP.values()}


@attr.s(auto_attribs=True, frozen=True, order=False, kw_only=True)
class Changelog:
    contents: str
    type: str = attr.ib()

    @type.validator
    def _check_type_valid(
        self,
        attribute: attr.Attribute[str],
        value: str,
    ) -> None:
        # no code coverage here: we either get this from the command line, which
        # requires the type to be from the CHANGELOG_TYPES, or from from_path(), which
        # will guess at the type, and fallback to text if unknown.
        #
        # however, if we somehow forget this and create the object willy-nilly,
        # this ValueError will leak through and stacktrace, which we want.
        if value not in CHANGELOG_TYPES:  # pragma: no cover
            raise ValueError(f"Changelog type {value} must be in {CHANGELOG_TYPES}")

    @classmethod
    def from_path(cls, path: Path) -> Changelog:
        normalized_changelog_suffix = path.suffix.lower()
        if normalized_changelog_suffix in CHANGELOG_SUFFIX_MAP:
            type = CHANGELOG_SUFFIX_MAP[normalized_changelog_suffix]
        else:
            log.warn(
                f"Unable to determine changelog type from extension for {path}, "
                'so assuming "text"'
            )
            type = "text"

        with path.open("r") as file:
            contents = file.read()

        return cls(
            type=type,
            contents=contents,
        )
