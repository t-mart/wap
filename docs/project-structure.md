# Project Structure

`wap` builds *packages*. A package is a group of addons which will be distributed together.

If you're just starting out, your package will only have one addon:

```mermaid
flowchart
    subgraph Package
    addon-a[Addon A]
    end
```

Larger projects will contain several addons with interconnected dependencies:

```mermaid
flowchart
    subgraph Package
    addon-a[Addon A]
    addon-b[Addon B] --> addon-a
    addon-c[Addon C] --> addon-a
    end
```

## Recommended File Layout

In your project root, you should keep your `wap.json` configuration file and your addon directories.

```text
MyProject/
├─── Addon A/
│    ├─── Main.lua
│    └─── Other.lua
├─── Addon B/
│    └─── API.lua
├─── README.md
└─── wap.json
```

!!! note

    The `.lua` files above are just examples. You do not need these file names.