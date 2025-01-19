"""
In testing, we want to see the data submitted to CF when uploading files. It's not
trivial to parse a multipart/form-data request, so this code assists in getting out the
bits of it that we want to verify.
"""

from __future__ import annotations

import json
from io import BytesIO
from typing import Any

import httpx
import multipart  # type: ignore
from attrs import frozen


@frozen(kw_only=True)
class CFUploadRequestContent:
    metadata: Any
    file_content_type: str
    file_name: str
    file_stream: bytes

    @classmethod
    def from_parse(cls, parse: multipart.MultipartParser) -> CFUploadRequestContent:
        metadata = json.loads(parse.get("metadata").raw)  # type: ignore
        file_part = parse.get("file")  # type: ignore
        file_content_type: str = file_part.content_type  # type: ignore
        file_name = file_part.filename  # type: ignore
        file_stream = file_part.raw  # type: ignore
        return CFUploadRequestContent(
            metadata=metadata,
            file_content_type=file_content_type,
            file_name=file_name,  # type: ignore
            file_stream=file_stream,  # type: ignore
        )

    @classmethod
    def from_request(cls, request: httpx.Request) -> CFUploadRequestContent:
        # need to peek to get the boundary
        boundary = request.content.splitlines()[0].removeprefix(b"--")
        return cls.from_parse(
            parse=multipart.MultipartParser(
                stream=BytesIO(request.content), boundary=boundary
            )
        )
