# Configuration

`wap` is configured with a JSON file.

When running commands that require a configuration file (and the a path to the configuration is not
explicitly provided), `wap` will look in the current directory for a
file named `wap.json`, and then, in any parent directory. If you have used git, then you are
already familiar.

## Full examples

- A minimal configuration:

    ```json
    {
      "name": "MyAddon",
      "version": "1.0.0",
      "wowVersions": {
        "mainline": "9.2.7",
      },
      "package": [
        {
          "path": "./MyAddon"
        }
      ]
    }
    ```

- A more fleshed out configuration with support for editor validation, publishing, TOC file
  generation, and multiple flavors:

    ```json
    {
      "$schema": "https://raw.githubusercontent.com/t-mart/wap/master/src/wap/schema/wap.schema.json",
      "name": "MyAddon",
      "version": "1.0.0",
      "description": "MyAddon enhances something...",
      "wowVersions": {
        "mainline": "9.2.7",
        "wrath": "3.4.0",
        "vanilla": "1.14.3"
      },
      "publish": {
        "curseforge": {
          "projectId": "523422",
          "slug": "myaddon",
          "releaseType": "release",
          "changelogType": "text"
        }
      },
      "package": [
        {
          "path": "./MyAddon",
          "toc": {
            "tags": {
              "Title": "MyAddon",
              "Author": "Me",
              "Notes": "Does this thing to the game"
            },
            "files": ["Init.lua", "Core.lua", "Extra.lua"]
          },
          "include": ["./LICENSE"]
        }
      ]
    }
    ```

## Schema

The JSON in a configuration file must be valid to
[a built-in schema](https://github.com/t-mart/wap/blob/master/src/wap/schema/wap.schema.json).

If your editor supports [JSON Schema](https://json-schema.org/) validation, make sure to set the
`$schema` field:

```json
{
    "$schema": "https://raw.githubusercontent.com/t-mart/wap/master/src/wap/schema/wap.schema.json"
}
```

### `name`

- Required
- Type: string

The name is what your [addon package](./project-structure.md#project-structure) is called.

It will be used in the following places:

- Output directory name (created when [building](./commands/build.md))
- Output zip name (created when [publishing](./commands/publish.md))
- Uploaded/downloaded file names on Curseforge

!!! example

    ```json
    "name": "My Addon"
    ```

### `author`

- Optional
- Type: string

The person/people that contributed to your package should be listed in this field.

This value is intended to document your project.

Additionally, in any [generated TOC files](./toc-gen.md), this value will be the default for
`Author` if it is not explicitly provided in the [`package[*].toc.tags`](#packagetoctags) section.

!!! example

    ```json
    "author": "Thrall"
    ```

!!! example

    ```json
    "author": "Amleth, Queen Gudrún, and Fjölnir the Brotherless"
    ```

### `description`

- Optional
- Type: string

A description of this package.

This value is intended to document your project.

Additionally, in any [generated TOC files](./toc-gen.md), this value will be the default for `Notes`
if it is not explicitly provided in the [`package[*].toc.tags`](#packagetoctags) section.

!!! example

    ```json
    "description": "This addon gives you more gold!"
    ```

### `version`

- Required
- Type: string

The version of your package. It does not have to follow any format.

It will be used in the same places as [`name`](#name).

Additionally, in any [generated TOC files](./toc-gen.md), this value will be the default for
`Version` if it is not explicitly provided in the [`package[*].toc.tags`](#packagetoctags) section.

!!! example

    ```json
    "version": "1.0.0"
    ```

### `wowVersions`

- Required
- Type: object with at least one key from `["mainline", "wrath", "vanilla"]` and values of the
  form `x.y.z` where `x`, `y`, and `z` are non-negative numbers

This object maps the flavors of the game your addon will support to the versions of those
flavors.

The recognized flavors are as follows:

| Flavor     | Description                                                             |
|------------|-------------------------------------------------------------------------|
| `mainline` | The mainline or "retail" flavor, which includes the latest expansions   |
| `wrath`    | The classic flavor that has slowly been evolving through old expansions |
| `vanilla`  | The classic flavor that only includes the first expansion               |

In any [generated TOC files](./toc-gen.md), this value (in its interface form) will be the default
for `Interface`.


!!! example

    ```json
    "wowVersions": {
      "mainline": "9.2.7"
    }
    ```

!!! warning

    If these versions fall behind, the WoW will claim your addon is out of date.

### `publish`

- Optional
- Type: object

A container for publish configurations.

#### `publish.curseforge`

- Optional
- Type: object

A container for Curseforge configuration.

##### `publish.curseforge.projectId`

- Required
- Type: string

The Curseforge project identifier, which identifies the package to publish to. You can find it on
your project page:

![Project id as found on Curseforge's "About Project" section](/assets/where-to-find-project-id.png)

You can create a new pacakge on [the website](https://www.curseforge.com/project/1/1/create).

!!! example

    ```json
    "publish": {
      "curseforge": {
        "projectId": "523422"
      }
    }
    ```

##### `publish.curseforge.changelogFile`

- Optional
- Type: string starting with `./`
- Mutually exclusive with [`publish.curseforge.changelogText`](#publishcurseforgechangelogtext)

The path to a changelog file, which describes how your addon package has changed over time.

Its path must be relative to the directory in which the configuration file exists. See
[Paths in the configuration](#paths-in-the-configuration)

Curseforge displays the changelog with every upload if it is provided.

!!! example

    ```json
    "publish": {
      "curseforge": {
        "projectId": "523422",
        "changelogFile": "./CHANGELOG.md"
      }
    }
    ```

##### `publish.curseforge.changelogText`

- Optional
- Type: string
- Mutually exclusive with [`publish.curseforge.changelogFile`](#publishcurseforgechangelogfile)

The literal text to use in the changelog.

Curseforge displays the changelog with every upload if it is provided.

!!! example

    ```json
    "publish": {
      "curseforge": {
        "projectId": "523422",
        "changelogText": "Added new feature X"
      }
    }
    ```

##### `publish.curseforge.changelogType`

- Optional, defaulting to `text`
- Type: string from `["markdown", "text", "html"]`

The markup language of the changelog contents.

!!! example

    ```json
    "publish": {
      "curseforge": {
        "projectId": "523422",
        "changelogText": "# Changelog\n\nSee the *website*...\n",
        "changelogType": "markdown"
      }
    }
    ```

##### `publish.curseforge.slug`

- Optional
- Type: string

A string identifier that identifies the Curseforge project.

You can find it in the URL of your project page. For example, if your project URL is
`https://www.curseforge.com/wow/addons/myaddon`, then your slug is `myaddon`.

This value lets wap print file URLS after publishing. Otherwise, an less-helpful file ID will be
printed.

!!! example

    ```json
    "publish": {
      "curseforge": {
        "projectId": "523422",
        "slug": "myaddon",
      }
    }
    ```

##### `publish.curseforge.releaseType`

- Optional
- Type: one of `release`, `beta`, or `alpha`

The release type to assign to uploads. `release` indicates the highest level of stability to users,
`alpha` the least, and `beta` in between.

This setting can be overriden by providing the [`--release-type`](./commands/publish.md#release-type)
option when running the publish command.

!!! example

    ```json
    "publish": {
      "curseforge": {
        "projectId": "523422",
        "releaseType": "beta",
      }
    }
    ```

### `package`

- Required
- Type: array with at least 1 item

A list of addon configurations.

#### `package[*].path`

- Required
- Type: string starting with `./`

The path to your addon directory. See [Project Structure](/project-structure/#project-structure) for
how your project should be laid out.

This value must be unique among all other addon paths provided.

Additionally, in any [generated TOC files](./toc-gen.md), this value will be the default for `Title`
if it is not explicitly provided in the [`package[*].toc.tags`](#packagetoctags) section.

!!! example

    ```json
    "package": [
      {
        "path": "./MyAddon"
      }
    ]
    ```

#### `package[*].toc`

- Optional
- Type: string starting with `./`

A container for TOC data. Providing this field turns enables [TOC file generation](./toc-gen.md).

##### `package[*].toc.tags`

- Optional
- Type: object

This object represents tag names and values in generated TOC files.

A tag can map any string name to any string value, just as long as the name does not contain a
space, a newline, or a colon.

`wap` recognizes the official tags in this section too. In some cases, the way the value is
expressed has been changed to better utilize JSON. You can see a description of these tags on the
[Wowpedia TOC format article](https://wowpedia.fandom.com/wiki/TOC_format).

| Name                             | Value Type      | Serializes To          |
|----------------------------------|-----------------|------------------------|
| `Title`                          | string          | string                 |
| `Title-<locale>`                 | string          | string                 |
| `Notes`                          | string          | string                 |
| `Notes-<locale>`                 | string          | string                 |
| `Author`                         | string          | string                 |
| `LoadOnDemand`                   | boolean         | `1`/`0`                |
| `RequiredDeps` or `Dependencies` | array of string | comma-separated string |
| `OptionalDeps`                   | array of string | comma-separated string |
| `LoadWith`                       | array of string | comma-separated string |
| `LoadManagers`                   | array of string | comma-separated string |
| `DefaultState`                   | boolean         | `enabled`/`disabled`   |
| `SavedVariables`                 | array of string | comma-separated string |
| `SavedVariablesPerCharacter`     | array of string | comma-separated string |

!!! example

    ```json
    "package": [
      {
        "path": "./MyAddon",
        "toc": {
          "tags": {
            "Title": "Cool Addon",
            "Notes": "This addon...",
            "My-Custom-Tag": "is this",
            "LoadOnDemand": true,
            "RequiredDeps": ["Foo", "Bar", "Baz"]
          }
        }
      }
    ]
    ```

!!! note

    The `Interface` and `Version` tags will be provided by `wap` according the
    [`wowVersion`](#wowversions) and [`version`](#version) sections, respectively. But, you can
    override them here if you really want to. See [TOC file generation](./toc-gen.md) for more
    information.

##### `package[*].toc.files`

- Optional
- Type: array

This array is the sequence of addon files that should be loaded for your addon. Note that,
regardless of what is listed, the entire addon `path` will be copied to the output directory -- this
is just for addon load ordering.

Paths will be resolved from the directory of the `path` field.

!!! example

    ```json
    "package": [
      {
        "path": "./MyAddon",
        "toc": {
          "files": [
            "First.lua",
            "Second.lua",
            "Third.lua"
          ]
        }
      }
    ]
    ```

!!! note

    Regardless of the files listed, all files under the `path` will be packaged. This section just
    declares the file load order.

#### `package[*].include`

- Optional
- Type: array

Use this field to include files outside the `path`. The strings provided must be either file paths
or file path globs. The glob syntax is that of Python's
[`pathlib.Path.glob`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob) function.

All paths will be resolved relative to the directory that contains the configuration file.

!!! example

    ```json
    "package": [
      {
        "path": "./MyAddon",
        "include": ["LICENSE"]
      }
    ]
    ```
