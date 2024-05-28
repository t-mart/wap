# `wap build`

`wap build [OPTIONS]`

Build addons into a playable, distributable package.

For each addon, building does 3 things:

- Copies source files, specified by [`package[*].path`](../configuration.md#packagepath), to the
  output directory.
- If specified by [`package[*].include`](../configuration.md#packageinclude), copies include files
  to the output directory.
- If [ToC file generation](../toc-gen.md) is configured by
  [`package[*].toc`](../configuration.md#packagetoc), generates ToC files in the output directory.

The above addon files will be placed in a package directory inside the output directory. This
directory will be named in the format of`<name>-<version>`, taking values as defined in your
configuration. For example, with a [`name`](../configuration.md#name) of `MyAddon` and
[`version`](../configuration.md#version) of `1.2.3`, the yielded output directory would be
`MyAddon-1.2.3`.

## Options

### `--watch`

`-w, --watch`

Enable "watch" mode, which will rebuild your addon any time a source file, an include file, or the
wap config file changes on your filesystem.

This mode is nice during development sessions because you do not need to run wap commands manually.
Paired with [`--link`](#-link), it becomes even more powerful.

You can press ++ctrl+c++ to exit this mode.

### `--link`

`-l, --link [auto|mainline|classic|vanilla]`

After building, symlink your addons in the output directory to the respective World of Warcraft
installation directory.

This is handy because you do not need to copy your files to those installation directories manually
to test them out in the game.

!!! note

    A symlink is a file that points to/targets another file. As far as World of Warcraft is
    concerned, the symlink is indistinguishable from the real file. If the symlink is deleted, the
    target file will be unaffected. See [Symbolic link](https://en.wikipedia.org/wiki/Symbolic_link)
    on Wikipedia for more information.

!!! warning

    Windows users will not be able to create symlinks by default. There are two options:

    - **Recommended** Enable developer mode by searching for "developer mode" in Settings and
      clicking the toggle.


        ![Turning on Developer Mode](../assets/developer-mode.png)

    - Run wap as an administrator.

The argument provided specifies to which installations links should be made: `auto` symlinks into
any found installations on your computer that are also compatible with the addon. `mainline`,
`classic`, `vanilla` symlink into those respective flavor's installation.

 Without an argument, `--link` runs as if `auto` was provided.

This option can be provided multiple times unless `auto` is also provided.

wap looks for installations in the following places:

| Platform | Default Installation Prefix                 |
|----------|---------------------------------------------|
| Windows  | `C:\Program Files (x86)\World of Warcraft\` |
| OSX      | `/Applications/World of Warcraft/`          |

| Flavor     | Addons Directory                          |
|------------|-------------------------------------------|
| `mainline` | `<prefix>/_retail_/Interface/Addons`      |
| `classic`    | `<prefix>/_classic_/Interface/Addons`     |
| `vanilla`  | `<prefix>/_classic_era_/Interface/Addons` |

If you've installed World of Warcraft into a custom location not listed above, you may point wap to
it with any of the [`--<flavor>-addons-path`](#-flavor-addons-path) options


### `--force-link`

`--force-link`

Lets the link operation succeed if something was already there when [`--link`-ing](#-link) by
deleting it first.

### `--<flavor>-addons-path`

- `--vanilla-addons-path DIRECTORY`
- `--classic-addons-path DIRECTORY`
- `--mainline-addons-path DIRECTORY`

When linking with [`--link`](#-link), override the default installation path with the directory path
provided.

!!! example

    ```shell
    wap build --classic-addons-path "D:/Games/World of Warcraft/_classic_/Interface/Addons"
    ```

### `--clean`

`--clean`

Before building, delete all files in the output addon directories. This can be helpful if you've
previously built a file that you no longer want to be in the package.

### `--config-path`

`--config-path FILE`

This path tells wap where to find your configuration, overriding the default of `wap.json`.

### `--output-path`

`--output-path FILE`

This path tells wap where to output the package, overriding the default of `dist`.

### `--help`

`--help`

Show the built-in help text and exit.
