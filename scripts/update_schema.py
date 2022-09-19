"""Download the latest wap schema to this project's source code directory."""

from pathlib import Path

import httpx

OUT_PATH = Path(__file__) / "../../src/wap/schema/wap.schema.json"
SRC_URL = (
    "https://raw.githubusercontent.com/t-mart/wap-json-schema/master/wap.schema.json"
)

response = httpx.get(SRC_URL)

with OUT_PATH.open("w") as outfile:
    outfile.write(response.text)

print(f"Wrote text from {SRC_URL} to {OUT_PATH.resolve()}")
print("Note that GitHub sometimes caches this content, so it may be out of date.")
print(
    "Perhaps as long as this 'Cache-Control` header: "
    f"{response.headers.get('Cache-Control', 'unknown')}"
)
