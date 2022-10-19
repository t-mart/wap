# `wap validate`

`wap validate [OPTIONS]`

Validate a configuration file.

If the file passes validation, print `valid` to stdout and return a 0 exit code. Otherwise, print
the problem to stderr, print `invalid` to stdout, and return a 1 exit code.

## Options

### `--config-path`

`--config-path FILE`

This path tells wap where to find your configuration, overriding the default of `wap.json`.

### `--help`

`--help`

Show the built-in help text and exit.
