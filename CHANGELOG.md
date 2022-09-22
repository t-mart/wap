# Changelog

## dev

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
