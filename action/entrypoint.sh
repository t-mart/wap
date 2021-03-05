#!/usr/bin/env bash

set -ex

wap package \
  --version "$WAP_VERSION" \
  --config-path "$WAP_CONFIG_PATH"

if [[ -n $WAP_CHANGELOG_TYPE ]]; then
    wap upload \
      --version "$WAP_VERSION" \
      --config-path "$WAP_CONFIG_PATH" \
      --release-type "$WAP_RELEASE_TYPE" \
      --curseforge-token "$WAP_CURSEFORGE_TOKEN" \
      --changelog-type "$WAP_CHANGELOG_TYPE" \
      --changelog-contents "$WAP_CHANGELOG_CONTENTS"
else
    wap upload \
      --version "$WAP_VERSION" \
      --config-path "$WAP_CONFIG_PATH" \
      --release-type "$WAP_RELEASE_TYPE" \
      --curseforge-token "$WAP_CURSEFORGE_TOKEN"
fi
