from __future__ import annotations

import json
from typing import BinaryIO, ClassVar, Optional

import attr
import requests

from wap.changelog import Changelog
from wap.exception import CurseForgeAPIException


@attr.s(kw_only=True, order=False, auto_attribs=True)
class CurseForgeAPI:

    api_token: str
    _version_map_cache: Optional[dict[str, int]] = attr.ib(
        default=None, init=False, eq=False
    )

    _SESSION: ClassVar[requests.Session] = requests.Session()
    _TOKEN_HEADER_NAME: ClassVar[str] = "X-Api-Token"
    _UPLOADED_FILE_URL_TEMPLATE: ClassVar[
        str
    ] = "https://www.curseforge.com/wow/addons/{slug}/files/{file_id}"

    RELEASE_TYPES: ClassVar[set[str]] = {"alpha", "beta", "release"}
    VERSION_ENDPOINT_URL: ClassVar[str] = "https://wow.curseforge.com/api/game/versions"
    UPLOAD_ENDPOINT_URL_TEMPLATE: ClassVar[
        str
    ] = "https://wow.curseforge.com/api/projects/{project_id}/upload-file"

    def upload_addon_file(
        self,
        *,
        project_id: str,
        archive_file: BinaryIO,
        display_name: str,
        changelog: Changelog,
        wow_version_id: int,
        release_type: str,
        file_name: str,
    ) -> int:
        """
        Uploads an addon file to Curseforge's WoW addon index.
        """
        metadata = self._create_release_metadata(
            changelog_contents=changelog.contents,
            display_name=display_name,
            version_id=wow_version_id,
            release_type=release_type,
            changelog_type=changelog.type,
        )

        resp = self._SESSION.post(
            url=self.UPLOAD_ENDPOINT_URL_TEMPLATE.format(project_id=project_id),
            headers={self._TOKEN_HEADER_NAME: self.api_token},
            data={"metadata": metadata},
            files={"file": (file_name, archive_file)},
        )

        if resp.status_code != requests.codes.ok:
            raise CurseForgeAPIException(
                f"Response from CurseForge during file upload has error status code "
                f"{resp.status_code}. Response body: {resp.text}"
            )

        return resp.json()["id"]  # type: ignore

    def get_version_id(self, *, version: str) -> int:
        # Since it's probably very common to upload 2 packages (a retail and classic),
        # we cache this response.
        if self._version_map_cache is None:
            resp = self._SESSION.get(
                url=self.VERSION_ENDPOINT_URL,
                headers={self._TOKEN_HEADER_NAME: self.api_token},
            )

            if resp.status_code != requests.codes.ok:
                raise CurseForgeAPIException(
                    f"Response from CurseForge during version lookup has error status "
                    f"code {resp.status_code}. Response body: {resp.text}"
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
            raise CurseForgeAPIException(
                f'Version "{version}" could not be found on CurseForge'
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
        return json.dumps(
            {
                "changelog": changelog_contents,
                "changelogType": changelog_type,
                "displayName": display_name,
                "gameVersions": [version_id],
                "releaseType": release_type,
            }
        )

    @classmethod
    def uploaded_file_url(cls, slug: str, file_id: int) -> str:
        return cls._UPLOADED_FILE_URL_TEMPLATE.format(
            slug=slug,
            file_id=file_id,
        )
