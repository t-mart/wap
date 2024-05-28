from copy import deepcopy
from typing import Any

_BASIC = {
    "$schema": "https://raw.githubusercontent.com/t-mart/wap/master/src/wap/schema/wap.schema.json",  # noqa: E501
    "name": "Package",
    "author": "Me",
    "version": "1.2.3",
    "wowVersions": {"mainline": "9.2.7", "classic": "4.4.0", "vanilla": "1.14.3"},
    "publish": {"curseforge": {"projectId": "1234", "slug": "thepackage"}},
    "package": [
        {
            "path": "./Addon",
            "toc": {
                "tags": {
                    "Title": "The title",
                    "Notes": "Notes for addon",
                },
                "files": ["Main.lua", "Extra.lua"],
            },
            "include": ["./LICENSE"],
        }
    ],
}


def get_basic_config() -> Any:
    return deepcopy(_BASIC)
