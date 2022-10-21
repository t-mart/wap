# TOC Generation

wap can generate TOC files for you addons. Generating TOC files:

- lets you support all desired flavors of WoW (Retail, Wrath, Classic) simultaneously
- has less error surface area than maintaining TOC files directly
- keeps your project [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) by auto-providing
  some tags from other parts of the configuration
- lets wap check that the TOC file is valid for the current project

TOC generation is enabled on a per-addon basis if you provide a
[`package[*].toc`](configuration.md#packagetoc) configuration section.

For example, if you have a configuration like this:

```json
{
  "$schema": "https://raw.githubusercontent.com/t-mart/wap/master/src/wap/schema/wap.schema.json",
  "name": "MyAddon",
  "version": "0.0.1",
  "author": "tim",
  "wowVersions": {
    "mainline": "9.2.7",
    "wrath": "3.4.0",
    "vanilla": "1.14.3"
  },
  "package": [
    {
      "path": "./MyAddon",
      "toc": {
        "tags": {
          "Title": "MyAddon",
          "Notes": "A cool addon"
        },
        "files": [
          "Main.lua"
        ]
      }
    }
  ]
}
```

The, wap will generate a TOC file for each flavor, including an "unflavored" fallback TOC, like
this:


=== "`MyAddon_Mainline.toc`"


    ```wowtoc
    ## Author: tim
    ## Interface: 90207
    ## Version: 0.0.1
    ## X-BuildDateTime: 2022-10-20T21:38:08.636618+00:00
    ## X-BuildTool: wap 0.9.0
    ## Title: MyAddon
    ## Notes: A cool addon

    Main.lua
    ```

=== "`MyAddon_Wrath.toc`"


    ```wowtoc
    ## Author: tim
    ## Interface: 30400
    ## Version: 0.0.1
    ## X-BuildDateTime: 2022-10-20T21:38:08.636618+00:00
    ## X-BuildTool: wap 0.9.0
    ## Title: MyAddon
    ## Notes: A cool addon

    Main.lua
    ```

=== "`MyAddon_Vanilla_.toc`"


    ```wowtoc
    ## Author: tim
    ## Interface: 11403
    ## Version: 0.0.1
    ## X-BuildDateTime: 2022-10-20T21:38:08.636618+00:00
    ## X-BuildTool: wap 0.9.0
    ## Title: MyAddon
    ## Notes: A cool addon

    Main.lua
    ```

=== "`MyAddon.toc`"


    ```wowtoc
    ## Author: tim
    ## Interface: 90207
    ## Version: 0.0.1
    ## X-BuildDateTime: 2022-10-20T21:38:08.636618+00:00
    ## X-BuildTool: wap 0.9.0
    ## Title: MyAddon
    ## Notes: A cool addon

    Main.lua
    ```

Note that they are all the same except for the interface number.

## Default Tags

If you do not provide an explicit value for some tags in
[`package[*].toc.tags`](./configuration.md#packagetoctags), then wap will provide defaults for you.
The table below lists the tags that wap provides and where they're sourced from.

| Tag               | Source                                                                                                |
|-------------------|-------------------------------------------------------------------------------------------------------|
| `Interface`       | The flavor's version from [`wowVersions`](./configuration.md#wowversions) setting (in interface form) |
| `Version`         | [`version`](./configuration.md#version) setting                                                       |
| `Author`          | [`author`](./configuration.md#author) setting                                                         |
| `Title`           | name of directory of [`package[*].path`](./configuration.md#packagepath) setting                      |
| `Notes`           | [`description`](./configuration.md#description) setting                                               |
| `X-BuildDateTime` | the UTC instant that the addon was built                                                              |
| `X-BuildTool`     | `wap` and its current version                                                                         |
