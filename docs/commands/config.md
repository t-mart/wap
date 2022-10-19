# `wap config`

`wap config [OPTIONS] PATH [VALUE]`

Get, set, or delete the JSON configuration value specified by JSON path `PATH`. When setting,
set the value to `VALUE`, which must be valid JSON (unless [`--raw`](#-raw) is set).

JSON paths access things inside your configuration. Objects can be accessed by property names and
arrays by their zero-based indexes. For example, `package.0.path` would access the `path` property
of the first index inside the top-level `package` property.

Mutations (`--set` and `--delete`) will only be written if they are valid.

If none of `--get`, `--set`, `--delete` is provided, `--get` will be assumed.

!!! note

    Your shell's quoting syntax may be different than what is displayed on this page.

## Options

### `--get`

`--get`

Print the configuration value at `PATH`.

Example:

```console
$ wap config --get "name"
"MyAddon"

$ wap config --get "wowVersions"
{
  "mainline": "9.2.7"
}
```

### `--set`

`--set`

Parse `VALUE` as JSON, set the configuration value at `PATH` to that JSON, print it, validate the
configuration as a whole, and save it.

Example:

```console
$ wap config --set "name" "MyGreatAddon"
"MyGreatAddon"

$ wap config --set "wowVersions" '{\"wrath\": \"1.2.3\"}'
{
  "wrath": "1.2.3"
}
```

### `--delete`

`--delete`

Delete the configuration value at `PATH`, validate the configuration as a whole, and save it.

Example:

```console
$ wap config --delete "package.0.toc.tags.DeleteMe"
```

### `--raw`

`--raw`

With `--get`, if the value at PATH is a string, print it without quotes.

Example:

```console
$ wap config --get "version"
"1.2.3"

$ wap config  --raw--get "version"
1.2.3
```

With `--set`, read VALUE as a string without quotes.

```console
$ wap config --set "version" '\"1.2.3\"'  # see the ugly quote escapes?
1.2.3

$ wap config  --raw --set "version" "1.2.3" # more intuitive
1.2.3
```
!!! note

    Setting with `--raw` only works when setting string values. For other value types, you must
    express them on your shell with proper quote escapes.

### `--config-path`

`--config-path FILE`

This path tells wap where to find your configuration, overriding the default of `wap.json`.

### `--help`

`--help`

Show the built-in help text and exit.
