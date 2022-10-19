# Configuration

`wap` is configured with a JSON file.

When running commands that require a configuration file (and the a path to the configuration is not
explicitly provided), `wap` will look in the current directory for a
file named `wap.json`, and then, in any parent directory. If you have used git, then you are
already familiar.

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

- Output directory name (created when building)
- Output zip name (created when publishing)
- Uploaded/downloaded file names on Curseforge

Example:

```json
"name": "My Addon"
```

### `author`

- Optional
- Type: string

The person/people that contributed to your package should be listed in this field.

If provided, this value will provide the `Author` tag in any [generated TOC files](./toc-gen.md),
unless the [`toc.tag`](#packagetoctags) section includes it.

Examples:

```json
"author": "Thrall"
```

```json
"author": "Amleth, Queen Gudrún, and Fjölnir the Brotherless"
```

### `version`

- Required
- Type: string

The version of your package. It does not have to follow any format.

It will be used in the same places as [`name`](#name).

Example:

```json
"version": "1.0.0"
```

### `wowVersions`

- Required
- Type: object with at least one key from `["mainline", "wrath", "vanilla"]` and values of the
  form `x.y.z` where x, y, and z are non-negative numbers

This object maps the flavors of the game your addon will support to the versions of those
flavors.

The recognized flavors are as follows:

| Flavor     | Description                                                             |
|------------|-------------------------------------------------------------------------|
| `mainline` | The mainline or "retail" flavor, which includes the latest expansions   |
| `wrath`    | The classic flavor that has slowly been evolving through old expansions |
| `vanilla`  | The classic flavor that only includes the first expansion               |

These flavor-version pairs will be used to determine which [TOC files to generate](./toc-gen.md) (if
any) and the `Interface` tag to include inside them.

!!! note

    If these versions fall behind, the game client will claim your addon is out of date.

Example:

```json
"wowVersions": {
  "mainline": "9.2.7"
}
```

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

The Curseforge project identifier, which identifies the package to update. You can find it on your
project page:

![Project id as found on Curseforge's "About Project" section](/assets/where-to-find-project-id.png)

If you do not have a project yet, you must create it manually on
[the website](https://www.curseforge.com/wow/addons).

Example:

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

Example:

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

Example:

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

Example:

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

This value will be used solely to print a convenient URL to the newly published file to the console.
If it is not provided, an less-helpful opaque file ID will be printed.

Example:

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

Example:

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

Example:

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

Example:

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

Example:

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


## Full example

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