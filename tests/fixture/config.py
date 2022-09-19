from copy import deepcopy
from typing import Any

_BASIC = {
    "$schema": (
        "https://raw.githubusercontent.com/t-mart/wap-json-schema/master/"
        "wap.schema.json"
    ),
    "name": "Package",
    "version": "1.2.3",
    "wowVersions": {"mainline": "9.2.7", "wrath": "3.4.0", "vanilla": "1.14.3"},
    "publish": {"curseforge": {"projectId": "1234", "slug": "thepackage"}},
    "package": [
        {
            "path": "./Addon",
            "toc": {
                "tags": {
                    "Title": "The title",
                    "Author": "Me",
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
