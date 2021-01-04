from __future__ import annotations

import json
from typing import BinaryIO, ClassVar, Optional

import attr
import requests

from wap.exception import CurseForgeAPIException, ReleaseException


@attr.s(kw_only=True, order=False, auto_attribs=True)
class CurseForgeAPI:

    api_token: str
    _version_map_cache: Optional[dict[str, int]] = attr.ib(
        default=None, init=False, eq=False
    )

    SESSION: ClassVar[requests.Session] = requests.Session()
    TOKEN_HEADER_NAME: ClassVar[str] = "X-Api-Token"
    VERSION_ENDPOINT_URL: ClassVar[str] = "https://wow.curseforge.com/api/game/versions"
    UPLOAD_ENDPOINT_URL_TEMPLATE: ClassVar[
        str
    ] = "https://wow.curseforge.com/api/projects/{project_id}/upload-file"
    CHANGELOG_TYPES: ClassVar[set[str]] = {"markdown", "text", "html"}
    RELEASE_TYPES: ClassVar[set[str]] = {"alpha", "beta", "release"}
    UPLOADED_FILE_URL_TEMPLATE: ClassVar[
        str
    ] = "https://www.curseforge.com/wow/addons/{addon_name}/files/{file_id}"

    def upload_addon_file(
        self,
        *,
        project_id: str,
        archive_file: BinaryIO,
        display_name: str,
        changelog_contents: str,
        wow_version_id: int,
        release_type: str,
        changelog_type: str,
        file_name: str,
    ) -> int:
        """
        Uploads an addon file to Curseforge's WoW addon index.
        """
        metadata = self._create_release_metadata(
            changelog_contents=changelog_contents,
            display_name=display_name,
            version_id=wow_version_id,
            release_type=release_type,
            changelog_type=changelog_type,
        )

        resp = self.SESSION.post(
            url=self.UPLOAD_ENDPOINT_URL_TEMPLATE.format(project_id=project_id),
            headers={self.TOKEN_HEADER_NAME: self.api_token},
            data={"metadata": metadata},
            files={"file": (file_name, archive_file)},
        )

        if resp.status_code != requests.codes.ok:
            raise CurseForgeAPIException(
                f"Response from CurseForge during file upload has status code "
                f"{resp.status_code}. Response body: {resp.json()}"
            )

        return resp.json()["id"]  # type: ignore

    def get_version_id(self, *, version: str, read_cache: bool = True) -> int:
        if self._version_map_cache is None or not read_cache:
            resp = self.SESSION.get(
                url=self.VERSION_ENDPOINT_URL,
                headers={self.TOKEN_HEADER_NAME: self.api_token},
            )

            if resp.status_code != requests.codes.ok:
                raise CurseForgeAPIException(
                    f"Response from CurseForge during version lookup has status code "
                    f"{resp.status_code}. Response body: {resp.json()}"
                )

            # this is a weird hoop, but the big wigs packager does the same thing:
            # hypothetically, the endpoint could return multiple versions that have the
            # same wow version, so just choose the one with the max id because it's
            # probably the latest.
            self._version_map_cache = {}
            for cf_version_obj in resp.json():
                name, id_ = cf_version_obj["name"], cf_version_obj["id"]
                if name not in self._version_map_cache:
                    self._version_map_cache[name] = id_
                else:
                    if self._version_map_cache[name] < id_:
                        self._version_map_cache[name] = id_

        if version not in self._version_map_cache:
            raise ReleaseException(
                f"Version {version} could not be found on CurseForge."
            )

        return self._version_map_cache[version]

    @classmethod
    def _create_release_metadata(
        cls,
        changelog_contents: str,
        changelog_type: str,
        display_name: str,
        version_id: int,
        release_type: str,
    ) -> str:
        if changelog_type not in cls.CHANGELOG_TYPES:
            raise ReleaseException(
                f'Changelog type "{changelog_type}" must be one of: '
                f"{','.join(cls.CHANGELOG_TYPES)}"
            )
        if release_type not in cls.RELEASE_TYPES:
            raise ReleaseException(
                f'Release type "{release_type}" must be one of: '
                f"{','.join(cls.RELEASE_TYPES)}"
            )

        return json.dumps(
            {
                "changelog": changelog_contents,
                "changelogType": changelog_type,
                "displayName": display_name,
                "gameVersions": [version_id],
                "releaseType": release_type,
            }
        )
