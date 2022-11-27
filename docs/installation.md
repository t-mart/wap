# Installation

## Installation

Before you get started, Python 3.11 or greater is required.
[Download it here](https://www.python.org/downloads/).

### pipx (Recommended)

The recommended way to install `wap` is with [pipx](https://pypa.github.io/pipx/). Its a little more
work than the [pip](#pip) method, but is safer and will prevent some nasty, hard-to-diagnose bugs.

First, install pipx by following [its installation
instructions](https://pypa.github.io/pipx/#install-pipx).

Then, you can then run:

```console
pipx install wow-addon-packager
```

### pip

To install with pip, run the following:

```console
pip install --upgrade --user wow-addon-packager
```

!!! warning

    Installing with pip creates the possibility of conflicts with other packages. The
    [pipx method](#pipx-recommended) does not have this issue.
