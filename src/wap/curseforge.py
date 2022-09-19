from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import BinaryIO, ClassVar, Literal, NewType, get_args

import httpx
from attr import frozen

from wap.console import warn
from wap.exception import (
    CurseForgeAPIException,
    EncodingException,
    PathMissingException,
)

GameVersionId = NewType("GameVersionId", int)
ChangelogType = Literal["text", "html", "markdown"]
CHANGELOG_TYPES: tuple[ChangelogType, ...] = get_args(ChangelogType)
ReleaseType = Literal["alpha", "beta", "release"]
RELEASE_TYPES: tuple[ReleaseType, ...] = get_args(ReleaseType)


def _raise_for_status(response: httpx.Response, activity_text: str) -> None:
    if response.status_code != httpx.codes.OK:
        raise CurseForgeAPIException(
            f"HTTP Error from CurseForge during {activity_text}: "
            f"'{response.status_code} {response.reason_phrase}'. Response body: "
            f"{response.text}"
        )


@frozen(kw_only=True)
class CurseForgeAPI:

    api_token: str

    _CLIENT: ClassVar[httpx.Client] = httpx.Client()
    TOKEN_HEADER_NAME: ClassVar[str] = "X-Api-Token"
    UPLOADED_FILE_URL_TEMPLATE: ClassVar[
        str
    ] = "https://www.curseforge.com/wow/addons/{slug}/files/{file_id}"

    VERSION_ENDPOINT_URL: ClassVar[str] = "https://wow.curseforge.com/api/game/versions"
    UPLOAD_ENDPOINT_URL_TEMPLATE: ClassVar[
        str
    ] = "https://wow.curseforge.com/api/projects/{project_id}/upload-file"

    def upload(
        self,
        *,
        project_id: str,
        archive_file: BinaryIO,
        display_name: str,
        changelog: Changelog,
        game_version_ids: Sequence[GameVersionId],
        release_type: str,
        file_name: str,
    ) -> int:
        """
        Uploads an addon file to Curseforge's WoW addon index and returns its file id.

        `display_name` is the name given to the upload and `file_name` is the name of
        file you download.
        """
        # multipart/form-data is different to me, so i looked into it:
        # in the request below, we set data and files. under the hood, these are
        # transformed to general key-value pairs:
        # {
        #   "metadata" -> <data value>,
        #   "file" -> <file value>
        # }
        # for transport, the entries are encoding according to spec. files get a bit of
        # extra treatment in that they need a content type and the data will come from
        # reading a file object.
        #
        # further, CF's API is a little weird in that they want the metadata value to
        # be a json-encoded object, even though multipart/form-data supports key-value
        # mapping itself -- i.e. they added another layer of encoding
        response = self._CLIENT.post(
            url=self.UPLOAD_ENDPOINT_URL_TEMPLATE.format(project_id=project_id),
            headers={self.TOKEN_HEADER_NAME: self.api_token},
            data={
                "metadata": json.dumps(
                    {
                        "changelog": changelog.text,
                        "changelogType": changelog.type_,
                        "displayName": display_name,
                        "gameVersions": game_version_ids,
                        "releaseType": release_type,
                    }
                )
            },
            files={"file": (file_name, archive_file, "application/zip")},
        )

        _raise_for_status(response, "upload")

        return response.json()["id"]  # type: ignore

    def get_version_map(self) -> Mapping[str, GameVersionId]:
        response = self._CLIENT.get(
            self.VERSION_ENDPOINT_URL, headers={self.TOKEN_HEADER_NAME: self.api_token}
        )
        _raise_for_status(response, "game version lookup")

        version_map: dict[str, GameVersionId] = {}
        for version_obj in response.json():
            version, id_ = version_obj["name"], version_obj["id"]
            if version not in version_map or version_map[version] < id_:
                version_map[version] = id_

        return version_map

    @classmethod
    def uploaded_file_url(cls, slug: str, file_id: int) -> str:
        return cls.UPLOADED_FILE_URL_TEMPLATE.format(
            slug=slug,
            file_id=file_id,
        )


@frozen(kw_only=True)
class Changelog:
    text: str
    type_: ChangelogType

    CHANGELOG_SUFFIX_MAP: ClassVar[Mapping[str, ChangelogType]] = {
        ".md": "markdown",
        ".markdown": "markdown",
        ".html": "html",
        ".txt": "text",
    }
    DEFAULT_CHANGELOG_TYPE: ClassVar[ChangelogType] = "text"

    @classmethod
    def from_text(cls, text: str, type_: ChangelogType | None = None) -> Changelog:
        if type_ is None:
            type_ = "text"
        return cls(type_=type_, text=text)

    @classmethod
    def from_path(cls, path: Path, type_: ChangelogType | None = None) -> Changelog:
        if type_ is None:
            suffix_normalized = path.suffix.lower()
            if suffix_normalized in cls.CHANGELOG_SUFFIX_MAP:
                type_ = cls.CHANGELOG_SUFFIX_MAP[suffix_normalized]
            else:
                warn(
                    f"Unable to determine changelog type from extension for {path}, "
                    f"so assuming {cls.DEFAULT_CHANGELOG_TYPE}"
                )
                type_ = cls.DEFAULT_CHANGELOG_TYPE

        try:
            contents = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as unicode_decode_error:
            raise EncodingException(
                f'Changelog file "{path}" cannot be decoded to utf-8: '
                f"{unicode_decode_error}"
            ) from unicode_decode_error
        except FileNotFoundError as file_not_found_error:
            raise PathMissingException(
                f"Changelog path {path} does not exist"
            ) from file_not_found_error

        return cls(
            type_=type_,
            text=contents,
        )

    @classmethod
    def suggest_changelog_type(cls, suffix: str) -> ChangelogType | None:
        return cls.CHANGELOG_SUFFIX_MAP.get(suffix.lower(), None)
