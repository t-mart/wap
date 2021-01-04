# wap (WoW Addon Packager)

- Builds and uploads your addons to CurseForge
- Uploads for retail and/or classic
- Installs your addons to your Addons folder for fast development feedback
- Generates TOC files for you (if you want, and you still have to configure what's in them)
- Is easily configurable

## Building

To build your addon into a single directory and create a zip archive of it

```bash
wap build
```

## Releasing

```bash
wap release
```

## Developer Install

```bash
wap dev-install <PACKAGE_NAME> /path/to/WoW/Interface/AddOns
```

## TODO

- tests
- print version info on start
  - any other nicer formatting for log output
  - consider stdout vs stderr?
- reconcile click error messaging and logging exception messaging
- localization via curseforge? big feature
- improve these docs and wiki docs
  - configuration schema like
  <https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions>
- version bumping
- gh actions
  - mypy
  - lint?
  - test
  - coverage upload
  - pip release on tag
- badges for readme
- Dockerfile
