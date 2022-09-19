# TODO Items

- ✅ Change configuration file format from YAML to JSON
  - JSON doesn't have a lot of the problems that YAML has. (JSON ain't perfect either, but less bad,
    imo)
    - StrictYAML is better (which we use)
  - JSON can have schemas, which:
    - assist in code completion
    - can validate json documents
  - oh gosh, i kinda just want it to be like package.json for node.
- ✅ Don't prefix configuration file path with a dot. This isn't supposed to be a hidden file. It's
  a first class citizen.
- ✅ Support all the new TOC formats that can co-exist. See
  <https://wowpedia.fandom.com/wiki/TOC_format> for more details. Currently supports retail, WotLK,
  BC and classic. (BC may get deprecated?)
  - Additionally, figure out how to tell curseforge about it.
- ✅ Not sure about this, but put version in the configuration file, making it the source of truth.
  - The repetition of `wap package --version <that_version>` and
    `wap upload --version <that_version>` is annoying.
    - then, we don't have to separate the package and upload steps
      - actually, they're still separate steps (because publishing should be an intentional act),
        but at least we don't have to double-declare the version
- ✅ Make a version management subcommand
  - print version
  - write new version from command line option (semver is too much work)
  - Actually better: make a config subcommand a la `git config`
    - `wap config version` prints version
    - `wap config version 1.2.3` sets version to 1.2.3
- ✅ Rename command `wap publish` (from `wap upload`).
- ⬜️ Ensure documentation all still works. We did some major version upgrade around here.
- ⬜️ Ensure documentation is valid. Some sweeping changes here.
- ⬜️ Write github action
- ✅ don't stack trace known exceptions
- ✅ Revisit watcher.
- ⬜️ Command to update wow versions to latest? Would require source of truth... curseforge? need
  token
