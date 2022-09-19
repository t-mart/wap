"""
A mock version of the CurseForge API
"""

import random
import re
import uuid
from collections.abc import Callable

from httpx import Request, Response
from respx.router import MockRouter

from wap.curseforge import CurseForgeAPI

# simulate actual authentication by declaring the only working token -- all others fail.
# callers will need to use this.
CURSEFORGE_TOKEN = str(uuid.uuid4())


def _check_auth(fn: Callable[[Request], Response]) -> Callable[[Request], Response]:
    def check(request: Request, **kwargs: str) -> Response:
        api_token = request.headers[CurseForgeAPI.TOKEN_HEADER_NAME]
        if not api_token:
            return Response(
                401,
                json={
                    "errorCode": 401,
                    "errorMessage": (
                        "You must provide an API token using the `X-Api-Token` header, "
                        "the `token` query string parameter, your email address and an "
                        "API token using HTTP basic authentication."
                    ),
                },
            )
        if not re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            api_token,
            flags=re.IGNORECASE,
        ):
            return Response(
                400,
                json={
                    "errorCode": 3,
                    "errorMessage": (
                        f"API token is malformed. Token provided: {api_token}."
                    ),
                },
            )
        if api_token != CURSEFORGE_TOKEN:
            return Response(
                403,
                json={"errorCode": 403, "errorMessage": "Invalid API token provided."},
            )
        return fn(request, **kwargs)

    return check


@_check_auth
def _version_response(_: Request, **kwargs: str) -> Response:
    # kwargs allows respx to pass in named regex groups as key-value pairs if they are
    # specified in the route
    return Response(
        200,
        json=[
            {"name": "9.2.7", "id": 1000},
            {"name": "9.2.7", "id": 1001},  # this one has higher id though
            {"name": "3.4.0", "id": 1002},
            {"name": "1.14.3", "id": 1003},
        ],
    )


@_check_auth
def _upload_response(_: Request, **kwargs: str) -> Response:
    return Response(200, json={"id": random.randint(1_000, 9_999)})


def setup_mock_cf_api(respx_mock: MockRouter) -> MockRouter:
    respx_mock.get(
        url="https://wow.curseforge.com/api/game/versions", name="versions"
    ).mock(side_effect=_version_response)
    respx_mock.post(
        url__regex=(
            r"https://wow.curseforge.com/api/projects/(?P<project_id>\d+)/upload-file"
        ),
        name="upload-file",
    ).mock(side_effect=_upload_response)
    return respx_mock
