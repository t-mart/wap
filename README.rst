wap (WoW Addon Packager)
========================

- Builds and uploads your addons to CurseForge
- Uploads for retail and/or classic
- Installs your addons to your Addons folder for fast development feedback
- Generates valid TOC files for you
- New project command to get started quickly
- Is easily configurable
- Tested on Windows, macOS, and Linux

.. contents:: Table of Contents

Usage
-----

Quickstart
**********

If you'd like to get started quickly, create a new project fast with:

.. code-block:: sh

  wap quickstart MyAddon

  # replace MyAddon with whatever you'd like

The above command will create a project directory structure like the following:

.. code-block:: none

  MyAddon               (your project's root directory)
  ├── MyAddon           (an addon directory that can be build/installed/uploaded)
  │   └── MyAddon.lua   (a Lua code file)
  ├── CHANGELOG.md      (where you describe changes over time to your project)
  ├── README.md         (where you document your project)
  └── .wap.yml          (the *wap* config file)

After this, you can begin developing your addon and using other *wap* commands.

Migrating from other pacakgers / Creating a new config file in an existing project
**********************************************************************************

The only file *wap* needs to run is a ``.wap.yml`` file. To create a new  file, run:

.. code-block:: sh

  wap new-config

The generated config file will contain a basic structure to get you started.

There are a few differences between how *wap* works and how other package managers work.
Please read around this document to learn about them.

Building
********

To build your addon into a single directory (with optional TOC generation) and create a
zip archive of it, run:

.. code-block:: sh

  wap build

Uploading
*********

To upload your addon to CurseForge, run:

.. code-block:: sh

  wap upload --addon-version 1.2.3 --curseforge-token "abc123"

Instead of providing ``--curseforge-token``, you may also set the environment variable
``WAP_CURSEFORGE_TOKEN``.

Some may prefer to use the current Git tag name as the version. You can just leverage
your shell to fill this option in with something like:

.. code-block:: sh

  wap upload \
    --version "$(git describe --always --tags)" \
    --release-type release \
    --curseforge-token "abc123"

Developer Install
*****************

To quickly test your addons out on your local WoW installation, run:

.. code-block:: sh

  wap dev-install --wow-addons-path "/path/to/WoW/_retail_/Interface/AddOns"

*wap* is smart in determining from your ``--wow-addons-path`` if it needs to install
the retail or classic build of your addon.

Instead of providing ``--wow-addons-path``, you may also set the environment variable
``WAP_WOW_ADDONS_PATH``.

Further Help
************

The *wap* command has more options than what has been shown above, and fully documents
that usage in its help text. View it with:

.. code-block:: sh

  wap --help
  wap build --help
  wap upload --help
  # ... etc

Installation
------------

1. Get Python 3.9 or greater. You can confirm this with ``python --version`` and
   verifying your version is at least that.

   Developers who do not have Python (or the right version) may get it easily from
   `<https://www.python.org/downloads/>`_.

2. Install *wap* from PyPI:

   .. code-block:: yaml

     pip install wow-wap

   Or, of course, you may install it into a virtual environment.

3. Verify *wap* can run:

   .. code-block:: yaml

     wap --version

The *wap* Configuration File
----------------------------

*wap* only needs one file to operate: a YAML file named ``.wap.yml``.

For new YAML authors, see
"`Learn YAML in five minutes. <https://www.codeproject.com/Articles/1214409/Learn-YAML-in-five-minutes>`_".

.. warning::
  For advanced YAML authors, it may be important to note that *wap* uses a subset of
  YAML called ``strictyaml``. This provides many benefits for users, but does
  `restrict some YAML features. <https://hitchdev.com/strictyaml/#design-justifications>`_.
  **The vast majority of users will not notice a difference!**

.. warning::
  In *wap* configuration files, all paths are treated as POSIX paths. The main highlight
  of this is that **all path separators (the slashes between directories and **
  **subdirectories and files) must be FORWARD SLASHES.** By choosing a standard,
  configuration files become cross-platform.

  All other paths, such as options to the ``wap`` command or outputs of ``wap`` are
  otherwise unaffected by this rule.

Sample ``.wap.yml`` Config File
*******************************

Here's a high-level, commented overview of a ``.wap.yml`` file:

.. code-block:: yaml

  # the name of your addon
  name: MyAddon

  # the versions of WoW your addon works on
  wow-versions:
    - 9.0.2
    - 1.13.6

  # If you want to upload to Curseforge
  curseforge:
    project-id: 123456  # found on your project page
    changelog: CHANGELOG.md  # a file relative to this config file with recent changes
    addon-name: myaddon  # found from your CurseForge URL

  # the contents of my addon
  dirs:
    - path: MyAddon  # a directory relative to this config file
      toc:  # TOC generation
        tags:  # metadata about your addon for WoW
          Title: MyAddon
          Notes: A great addon for WoW
          Author: Me
          DefaultState: Enabled
          LoadOnDemand: 0
          Dependencies: AnotherAddon
          X-My-Metadata-Tag: foo
        files:  # the files to load, in order, for your addon
          - Init.lua
          - Core.lua

Syntax
******

``name``
^^^^^^^^

Required
  Yes

Type
  ``string``

Description
  The name of your packaged addon. This name will be used to:

  - To name the build directories for your addon
  - To name the ``.zip`` files of your addon as they appear on your system and on
    Curseforge.

``wow-versions``
^^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``sequence``

Description
  The versions of World of Warcraft that your addon targets. *wap* will create different
  builds for each version in the output directory.

  Each version must be in the form "``x.y.z``", where ``x``, ``y``, and ``z`` are
  integers.

  You must at least supply one of these, and can at most supply two (for retail and
  classic).

  *wap* uses these versions for a few things:

  - To properly generate your TOC file with the right ``## Interface`` tag
  - To ``dev-install` the right build into the right WoW AddOns path (e.g. a classic
    addon build should not go into a `World of Warcraft/_retail_/Interface/AddOns`
    directory.
  - To designate which version your addon supports on CurseForge

  *wap* uses simple heuristics to decide if a version is retail or classic. Conversely,
  it cannot determine if a version actually exists or not.

``curseforge``
^^^^^^^^^^^^^^

Required
  No

Type
  ``map``

Description
  If you want to upload your project to CurseForge, include this section.

``curseforge.project-id``
^^^^^^^^^^^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``string``

Description
  The project id as found on your CurseForge addon's page.

  .. image:: docs/project-id.png
    :alt: Where to find your CurseForge project id

``curseforge.changelog``
^^^^^^^^^^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``string``

Description
  The path *relative to the config file* of your changelog file. This file should
  contain a helpful history of changes to your addon over time. (There are no strict
  requirements for the contents of this file, but it must exist. You may leave it
  blank if you wish, but it will not help your users.)

  CurseForge requires changelog contents to be provided with file uploads, and will
  display this content on the file's page.

  The extension of this file is used to determine what ``changelogType`` to provide in
  the upload request, which is also required. CurseForge currently supports three types:

  - ``markdown``
  - ``html``
  - ``text``

  *wap* will try to chose the correct ``changelogType`` based on the extension of the
  file you provide here. It does so according to the following mapping:

  +-----------------+-------------------+
  | File Extension  | ``changelogType`` |
  +=================+===================+
  | ``.md``         | ``markdown``      |
  +-----------------+-------------------+
  | ``.markdown``   | ``markdown``      |
  +-----------------+-------------------+
  | ``.html``       | ``html``          |
  +-----------------+-------------------+
  | ``.txt``        | ``text``          |
  +-----------------+-------------------+
  | All other cases | ``text``          |
  +-----------------+-------------------+

``curseforge.addon-name``
^^^^^^^^^^^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``string``

Description
  The string of the name of your addon as it is found in your addon's CurseForge
  URL.

  While not strictly necessary, if this is not provided, *wap* cannot provide a URL for
  your uploads in its output. (This is a limitation of the CurseForge API. *wap* cannot
  retrieve this name for you.)

  For example, if your addon's URL is
  ``https://www.curseforge.com/wow/addons/myaddon``, then you would use the string
  ``myaddon`` here.

``dirs``
^^^^^^^^

Required
  Yes

Type
  ``sequence``

Description
  A sequence of directories to include in your packaged addon.

  Many small addons will only contain a single ``dirs`` entry, but more complex ones
  will have many.

``dirs[*].path``
^^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``string``

Description
  The path *relative to this config file* of the directory you'd like to include in your
  packaged addon.

  This cannot be a file -- it must be a directory because WoW only recognizes
  addons in their own directories in ``Interface/AddOns``.

``dirs[*].toc``
^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``map``

Description
  A mapping of ``tags`` and ``files`` from which to generate your TOC file.

  For more information on why TOC file generation is a good thing, see
  `Why generate TOC files?`_.

``dirs[*].toc.tags``
^^^^^^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``map``

Description
  A mapping of key-value pairs to include in the generated TOC file. The keys and values
  will be interpreted as strings.

  Use this section to provide things like the ``Title``, ``Notes`` (description), and
  any other WoW-specified tags. A full list of supported tags may be found at the
  WoW Gamepedia
  `TOC format article <https://wow.gamepedia.com/TOC_format#Display_in_the_addon_list>`_.

  To demonstrate, a ``tags`` section that looks like this:

  .. code-block:: yaml

    tags:
      Title: MyAddon
      Notes: This is my addon

  will produce a TOC file with this content:

  .. code-block:: none

    ## Title: MyAddon
    ## Notes: This is my addon

  **Importantly, you do not need to provide the ``Interface`` and ``Version`` tags!**
  *wap* can generate these for you from the WoW version you specified in
  ``wow-versions[*].version`` and the version your supply when you ``wap upload``.
  If you do provide these tags, *wap* will do as you say, but will emit a warning and
  likely break some of its guarantees.

  You may add custom tags here too, if you wish. Custom tags may be retrieved with the
  |GetAddOnMetadata function|_, but only if they are prefixed with ``X-``. *wap* will
  emit a warning about custom tags without this prefix.

  .. |GetAddOnMetadata function| replace:: ``GetAddOnMetadata`` function
  .. _GetAddOnMetadata function: https://wow.gamepedia.com/API_GetAddOnMetadata

``dirs[*].toc.files``
^^^^^^^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``sequence``

Description
  An sequence of paths *relative to the* ``path`` *of this directory* that specify the
  Lua (or XML) files your addon should load. The order of this sequence is respected.

  To demonstrate, a ``files`` section that looks like this:

  .. code-block:: yaml

    files:
      - Init.lua
      - Core.lua

  will produce a TOC file with this content:

  .. code-block:: none

    Init.lua
    Core.lua

  Additionally, the files here are validated to ensure they actually exist. File that do
  not exist almost certainly indicate an bug, so *wap* will abort if such a case is
  found and print the missing file.

Why?
----

Why make another addon tool?
****************************

*wap* is a reimagining of how developers create addons. The most popular current
solution in this space is probably the
`BigWigsMods/packager <https://github.com/BigWigsMods/packager>`_ project. While I do
think they've done some excellent work (and I think they are just improving on prior
conventions), there are some pain points:

- Substitution directives (e.g. ``--@keyword@``) are

  * difficult to read, write, and maintain
  * slow to process (some of my builds take
    `7+ minutes at this step <https://github.com/t-mart/ItemVersion/runs/1864902187>`_!)
  * impossible to run `static analysis <https://github.com/mpeterv/luacheck>`_ on

- Dependencies (``externals``) should not be source code repositories

- The complexity of the program has outgrown the Bash scripting language and is
  therefore difficult to read, write and maintain.

Why not implement/support substitution directives like ``--@retail@``?
*************************************************************************

Let's compare two examples, one using substitution directives and one using the WoW API:

.. code-block:: lua

  -- WITH SUBSTITUTION DIRECTIVES
  local wowVersion = "retail"
  --[===[@non-retail@
  local wowVersion = "classic"
  --@end-non-retail@]===]
  print("Hi, I'm running on " .. wowVersion .. " WoW!")

.. code-block:: lua

  -- WITH THE WOW API
  local wowVersion = "retail"
  if WOW_PROJECT_ID == WOW_PROJECT_CLASSIC then
    wowVersion = "classic"
  end
  print("Hi, I'm running on " .. wowVersion .. " WoW!")

With substitution directives, I see:

- Lua code comments overloaded into another language with its own special syntax and
  keyword names.
- The ability to introduce bugs in the lua code itself, because lua static analyzers
  like `luacheck <https://github.com/mpeterv/luacheck>`_ obviously do not try to parse
  comments.

On the other hand, with the WoW API version, I see:

- Clear, parseable Lua code that can be statically analyzed.
- A leveraging of the API that WoW exposes.

And this is just Lua. Substitution directives also exist for TOC and XML files:

- The main case for substitution in TOC files is to handle the ``Interface`` tag, which
  *wap* can do for you.
- For XML, there may be a valid use case. But I'd counter that you should not be writing
  it for your addons because WoW Lua code can do everything that WoW XML documents can.
  So why would you want to put yourself through that?

In closing, the main point is here is that there are programmatic ways in your Lua code
to do everything that substitution directives do, but in a better way, and TOC file
generation is handled by *wap* itself.

Why generate TOC files?
***********************

There are two main reasons:

- Cut down on duplication. If you need to upload a retail AND a classic version, you'd
  otherwise need to create 2 nearly identical TOC files that only differ in their
  ``Interface`` tags.

  So instead, by centralizing TOC contents into the ``.wap.yml``, *wap* can generate
  your TOC file with your tags and files AND the correct ``Interface`` for the version
  of WoW you are targeting. *wap* also does this for the ``Version`` tag (the version of
  your addon), which is passed in as a command line argument when you run *wap*.

- TOC validation. *wap* validates that:

  * Any files listed actually exist within that folder
  * Any custom tags are prefixed with ``X-``, which is necessary for them to be
    retrievable by
    `GetAddOnMetadata <https://wowwiki-archive.fandom.com/wiki/API_GetAddOnMetadata>`_.
    Non-prefixed tags do not cause an error for WoW, but on the other hand, they are
    also invisible to WoW.

During early development, *optional* TOC generation was considered. But, it was
ultimately disallowed for the following reasons:

- *wap* would do no validation of the tags and files in your TOC file. For example, you
  may include a file that does not exist or include a custom tag without the ``X-``
  prefix. This would likely cause bugs.
- *wap* would not add your ``## Version: <version>`` tag. Therefore:
  * The version in your TOC file will **not** necessarily be equal to the
    ``--addon-version`` that you supply with commands.
  * The version may not even exist in your TOC file, which is not an error, but is
    a very unconventional software practice.
- *wap* would not add your ``## Interface: <interface>`` tag. Again, it may not even
  exist in your TOC file, which will probably cause WoW to believe it is out-of-date.
- If you're uploading a classic and a retail version, but are using a fixed TOC file in
  the directories that are zipped, then the classic and retail zip files will be
  identical. CurseForge specifically identifies this case and will reject one of the
  uploads after processing it.

So, TOC generation is probably a good thing. If you encounter a case where the *wap* TOC
generation is insufficient for what you are trying to do, please create an issue.

Why not automatically get my addon's version number from my VCS?
****************************************************************

In the spirit of keeping *wap* (and addon development in general!) accessible, I don't
want to force your hand on your addon's development process and tooling.

Besides, if you insist, you can extract a version from your VCS using a command like the
uploading_ section suggests.

Why not support pulling in dependencies (``externals``) from other repositories?
********************************************************************************

For a variety of reasons:

- Source code repositories are not releases. That is not their purpose. Source code
  repositories are filled with all sorts of things like READMEs and ``.gitignore`` files
  and tests and documentation and the list the goes on and on... And none of that has to
  do with the Lua code that you're really after.

  That Lua code belongs in a deliberate release asset (file/zip/etc) by the project
  owner, cleansed and packaged in a way you can include in your addon.

  Unfortunately, Lua does not have a distribution format and/or package repository (e.g.
  PyPI for Python, Maven Central for Java, Docker Hub for Docker, etc). Maybe you are
  lucky and the author of your dependency has created a GitHub Release asset that would
  serve you better than the repository itself.

- Even if you do have dependency repository that's tolerably clean and packaged in its
  natural form, that repository is actually a development-time dependency, not a
  release-time dependency like other addon packagers imply. It needs to be *inside* your
  codebase while you write your code. Otherwise, you're coding on hope.

  * Other addon packagers don't even require a commit hash/tag to be specified, so you
    can't even be sure what of what code will be included with your addon in those
    cases. Dependencies shouldn't be changing *at all* unless you've deliberately
    upgraded them.

- It slows down your release process to redownload dependencies.

- Finally, this is just feature bloat for *wap*. It's excessive to write a ``git clone``
  and/or ``svn checkout`` runner when you can run those tools better yourself. It opens
  up a huge surface area of support if *wap* needs to be able to run those tools itself.

TLDR: *wap* could, but it won't. **Copy your dependencies into your project from an
official release, or from the dependency's repository if that is all they offer.**

Why not support WoWInterface uploads?
*************************************

The momentum of the WoW community points towards CurseForge.

I actually have written WoWInterface support, but removed it because I don't think many
users would want it.

If I'm wrong about that, please create an issue and we can discuss and reassess.

Why not support GitHub Release uploads?
***************************************

- It requires that a tag is exists in the repository, which is a prerequisite for a
  GitHub release. I don't want to force your hand on your development process.

- It requires *wap* to interact with your Git repository, which would include at the
  very least:

  * knowing Git compatible versions

  * requiring *wap* to be run from within the addon repository, or adding another
    command line option to specify it.

- It adds the GitHub API itself as a dependency, which is a moving target.

- It's something that other tools already do better.

Instead, I kindly suggest you incorporate something like
`Github CLI <https://cli.github.com/>` or
`upload-release-asset <https://github.com/actions/upload-release-asset>`_ into your
build process in conjunction with *wap* if you want this feature. For *wap*, it's too
much bloat for too little gain.

Contributing
------------

See `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.

TODOs
-----

- localization via curseforge?
- gh actions
   * mypy
   * lint?
   * test
   * coverage upload
   * pip release on tag
- badges for readme
- little gif that shows how it works
- Dockerfile
- Dockerfile github action `<https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action>`_
