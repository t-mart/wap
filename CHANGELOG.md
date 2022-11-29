# Changelog

## 0.10.11

- Fix dependency issue

## 0.10.10

- Bump HTTP timeout from 5 to 15 seconds to make uploads less likely to fail.

## 0.10.9

- Fix `--force-link` deleting of symlinks.

## 0.10.7

- When linking during builds, let users forcibly link if the link path already exists with the
  `--force-link` option. This will delete the file/directory that was already there.

## 0.10.6

(woops forgot to update these)

- Change configuration file format from YAML to JSON
- Use JSON schema for validation, available at `src/wap/schema/wap.schema.json`
- Don't prefix default configuration file name with a dot
- Build TOC files for all flavors in one package instead of one flavor per package
- Add, remove, rename some commands
- Move documentation to Material for MkDocs
- Rewrite almost everything

## 0.9.0

- Force UTF-8 encoding for configuration and changelog files, and gracefully error on any other
encoding.
