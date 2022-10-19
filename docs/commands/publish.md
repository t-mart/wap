# `wap publish`

`wap publish [OPTIONS]`

Upload packages to Curseforge that were previously built with [`wap build`](../build.md). The
package will be added to the file of your project, configured with
[`publish.curseforge.projectId`](../configuration.md#publishcurseforgeprojectid)

A changelog will be uploaded with your package, as configured by
[`publish.curseforge.changelogFile`](../configuration.md#publishcurseforgechangelogfile) or
[`publish.curseforge.changelogText`](../configuration.md#publishcurseforgechangelogtext). If neither
are provided, the changelog will be empty.

Curseforge supports Markdown, HTML, and plaintext formatting for changelogs. The format may be
specified explicitly with
[`publish.curseforge.changelogType`](../configuration.md#publishcurseforgechangelogtype). In the
case of using a changelog file with `publish.curseforge.changelogFile`, the format may be guessed
from the file path's extension. If no format can be guessed or if the type is not provided,
plaintext will be assumed.

If you have provided [`publish.curseforge.slug`](../configuration.md#publishcurseforgeslug),
wap will generate a nice URL of the upload.

## Options

### `--curseforege-token`

`--curseforge-token TOKEN`

Your token authorizes your publish request. This should be considered a secret (and therefore,
should not be saved in source code!).

You can create new tokens at Curseforge's
[API token page](https://authors.curseforge.com/account/api-tokens)

### `--release-type`

`-r, --release-type [alpha|beta|release]`

The release type communicates to users the level of stability of your addon. `release` indicates the
highest level, `alpha` the least, and `beta` in between.

This option overrides the
[`publish.curseforge.releaseType`](../configuration.md#publishcurseforgereleasetype) configuration
setting. If neither are set, this command defaults to `alpha`.

### `--config-path`

`--config-path FILE`

This path tells wap where to find your configuration, overriding the default of `wap.json`.

### `--output-path`

`--output-path FILE`

This path tells wap where to find a previously built package, overriding the default of `dist`.

### `--help`

`--help`

Show the built-in help text and exit.
