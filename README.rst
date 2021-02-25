wap (WoW Addon Packager)
========================

.. image:: https://github.com/t-mart/wap/actions/workflows/ci.yml/badge.svg?branch=master
   :target: https://github.com/t-mart/wap/actions/workflows/ci.yml
   :alt: GitHub Actions status for master branch

.. image:: https://codecov.io/gh/t-mart/wap/branch/master/graph/badge.svg?token=AVOA4QWTBL
   :target: https://codecov.io/gh/t-mart/wap
   :alt: Code Coverage on codecov.io

.. image:: https://img.shields.io/pypi/v/wow-addon-packager
   :target: https://pypi.org/project/wow-addon-packager/
   :alt: Latest release on PyPI

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code styled with black

.. image:: https://img.shields.io/github/license/t-mart/wap
   :target: https://github.com/t-mart/wap/blob/master/LICENSE
   :alt: MIT licensed

|

*wap* is a user-friendly World of Warcraft addon packager.

.. image:: https://raw.githubusercontent.com/t-mart/wap/master/docs/demo.gif
   :alt: wap demo

Features
--------

- Builds and uploads your addons to CurseForge
- Creates retail or classic WoW addons, or both!
- Installs your addons to your Addons folder for fast development feedback
- Generates valid TOC files automagically
- Sets up new addon projects quickly, ready to go with one command
- Consolidates all configuration in one easy-to-edit file
- Supports Windows, macOS, and Linux

Table of Contents
-----------------

.. contents::

Getting started
---------------

Installation
************

1. `Download <https://www.python.org/downloads/>`_ and install Python
2. Install *wap* with pip:

   .. code-block:: console

      $ pip install -U wow-addon-packager

Create a new addon project
**************************

.. code-block:: console

   $ wap quickstart MyAddon  # or whatever name you'd like!

and answer the prompted questions. Don't worry too much about your answers -- you can
always change them later in your configuration file.

Building
********

Building your addon packages it up into a single directory and creates a zip file of it.

.. code-block:: console

   $ wap build

Developer Install
*****************

Instead of copy-pasting folders into your WoW installation to test out your work, *wap*
can do that for you:

.. code-block:: console

   # Windows
   $ wap dev-install --wow-addons-path "C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns"

   # macOS
   $ wap dev-install --wow-addons-path "/Applications/World of Warcraft/_retail_/Interface/AddOns"

Change ``_retail_`` to ``_classic_`` if you want to install your classic build.

*wap* is smart in determining from your ``--wow-addons-path`` if it needs to install
the retail or classic build of your addon.

Uploading
*********

.. code-block:: console

   $ wap upload --addon-version 0.0.1 --curseforge-token "<your-token>"

You can generate a new token at `<https://authors.curseforge.com/account/api-tokens>`_.

Further Help
************

*wap* has more commands and options than what has been shown above, and fully documents
that usage in its help text. View it with:

.. code-block:: console

   $ wap --help
   $ wap build --help
   $ wap upload --help
   # ... etc

The *wap* Configuration File
----------------------------

*wap* only needs one file to operate: a YAML file named ``.wap.yml``.

For new YAML authors, see `What is YAML? <https://blog.stackpath.com/yaml/>`_.

.. warning::
  For advanced YAML authors, it may be important to note that *wap* uses a subset of
  YAML called ``strictyaml``. This provides many benefits for users, but does
  `restrict some buggy YAML features. <https://hitchdev.com/strictyaml/#design-justifications>`_.
  There's a good chance you won't even notice a difference.

.. warning::
  In *wap* configuration files, all paths are treated as POSIX paths. The main takeaway
  of this is that path separators (the slashes between directories and subdirectories
  and files) are **forward slashes** (``/``). By choosing a standard, configuration
  files become cross-platform.

  .. code-block:: yaml

     path/to/my.lua    # GOOD, only forward slashes
     path\to\my.lua    # bad
     path/to\my.lua    # bad

Sample Config File and Directory Structure
******************************************

Here's a high-level, commented example of a ``.wap.yml`` file:

.. code-block:: yaml

  # the name of your addon, can be anything you like
  name: MyAddon

  # a list of versions of WoW your addon works on
  wow-versions:
    - 9.0.2
    - 1.13.6

  # If you want to upload to CurseForge, include this section
  curseforge:
    # found on your project page
    project-id: 123456
    # change history file, optional
    changelog: CHANGELOG.md
    # found from your CurseForge URL
    # ex: https://www.curseforge.com/wow/addons/myaddon -> "myaddon"
    addon-name: myaddon

  # a list of directories that will be packaged up
  dirs:
    - path: MyDir  # an addon directory
      toc:  # TOC generation
        tags:  # metadata about your addon for WoW
          Title: MyAddon
          Notes: A great addon for WoW
          Author: Me
          X-CustomTag: CustomValue
        files:  # the files to load, in order, for your addon, as found inside MyDir
          - Init.lua
          - MySubDir/Sub.lua

And heres a directory structure that this config could work with:

.. code-block::

   MyProject                # your project directory
   ├── MyDir                # your addon directory (dirs[*].path in config)
   |   ├── Init.lua         # A Lua code file (dirs[*].toc.files in config)
   |   └── MySubDir         # A subdirectory in your addon directory
   │       └── Sub.lua      # Another Lua code file (dirs[*].toc.files in config)
   ├── CHANGELOG.md         # changelog file (curseforge.changelog in config)
   ├── README.md            # readme documentation
   └── .wap.yml             # configuration file

Syntax
******

``name``
^^^^^^^^

Required
  Yes

Type
  ``string``

Description
  The name of your packaged addon. This name will be used to name the build directories
  and zip files for your addon (as well as the zip file users download on CurseForge).

  You can name this anything you want.

``wow-versions``
^^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``sequence``

Description
  The versions of World of Warcraft that your addon supports. *wap* will create
  different builds for each version in the output directory.

  Each version must be in the form "``x.y.z``", where ``x``, ``y``, and ``z`` are
  non-negative integers.

  You must at least supply one of these, and can at most supply two (for retail and
  classic).

  *wap* uses these versions for a few things:

  - To properly generate your TOC file with the right ``## Interface`` tag
  - To mark on CurseForge which version your addon supports
  - To ``dev-install`` the right build into the right WoW AddOns path. For example a
    classic addon build should not go into a
    ``World of Warcraft/_retail_/Interface/AddOns`` directory.

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
  The project id as found on your CurseForge addon's page. This field tells wap
  what addon page to upload to.

  .. image:: https://raw.githubusercontent.com/t-mart/wap/master/docs/project-id.png
    :alt: Where to find your CurseForge project id

``curseforge.changelog-file``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Required
  No

Type
  ``string``

Description
  The path *relative to this config file* of your changelog file. This file should
  contain a helpful history of changes to your addon over time. There are no
  requirements for the contents of this file -- it just needs to exist. You may leave
  it blank if you're just starting out.

  See the `Sample Config File and Directory Structure`_ section for an example on where
  this file is expected to be inside your project.

  CurseForge also requires a changelog type, which indicates the format of your
  log contents. They support the following three:

  - ``markdown``
  - ``html``
  - ``text``

  *wap* will try to chose the correct format based on the extension of the file you
  provide for this field. It does so according to the following mapping:

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

  Also note that this field is optional. But if you do not provide it, you must use the
  ``--changelog-contents`` and ``--changelog-type`` options when you run the upload
  command: Curseforge requires this data. It accompanies each file uploaded to the site.

  (CurseForge aside, maintaining a changelog file is a good practice. This is helpful
  information for both your users and collaborators.)

``curseforge.slug``
^^^^^^^^^^^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``string``

Description
  The string of the name of your addon as it is found in your addon's CurseForge
  URL.

  While not strictly necessary, this helps *wap* provide better output for you in the
  form of URLs that you can copy-paste into your browser.

  For example, if your addon's URL is
  ``https://www.curseforge.com/wow/addons/mycooladdon``, then you would use the string
  ``mycooladdon`` here.

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

  See the `Sample Config File and Directory Structure`_ section for an example on where
  this directory is expected to be inside your project.

  This cannot be a file -- only directories are installable into WoW addons folders.

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
  Custom tags can be added too, and should be prefixed with ``X-``.

  To demonstrate, a ``tags`` section that looks like this:

  .. code-block:: yaml

    tags:
      Title: MyAddon
      Notes: This is my addon
      X-Custom-Tag: CustomValue

  will produce a TOC file with this content:

  .. code-block::

    ## Title: MyAddon
    ## Notes: This is my addon
    ## X-Custom-Tag: CustomValue

  .. warning::
    **You should not provide the ``Interface`` and ``Version`` tags!** *wap* generates
    those tags for you. You can override them, but it is not recommended.

``dirs[*].toc.files``
^^^^^^^^^^^^^^^^^^^^^

Required
  Yes

Type
  ``sequence``

Description
  A sequence of paths *relative to* `dirs[*].path`_  that specify the Lua (or XML) files
  your addon should load. The order of this sequence is respected in the generated TOC
  file.

  See the `Sample Config File and Directory Structure`_ section for an example on where
  these files are expected to be inside your project.

  To demonstrate, a ``files`` section that looks like this:

  .. code-block:: yaml

    files:
      - Init.lua
      - Core.lua

  will produce a TOC file with this content:

  .. code-block::

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
solution is probably the `packager <https://github.com/BigWigsMods/packager>`_ project,
I think there are some design flaws that needed revisiting. Namely, it:

- Encourages the use substitution directives (e.g. ``--@keyword@``) to solve problems,
  which are:

  * difficult to read, write, and maintain
  * slow to process (some of my builds take
    `7+ minutes at this step <https://github.com/t-mart/ItemVersion/runs/1864902187>`_!)
  * impossible to run `static analysis <https://github.com/mpeterv/luacheck>`_ on

- Conflates for dependencies (``externals``) and source code repositories. They are not
  the same thing.
- Presumes your entire repository should be packaged up, which is awkward and
  heavy-handed for most modern projects and requires ``ignore``-ing many files.
- Mandates the use of certain version control processes, which are inaccessible for
  beginning developers.
- Reads its configuration from several files (``.pkgmeta`` and ``.toc`` files).

Why not implement substitution directives like ``--@retail@``?
**************************************************************

Let's compare two examples:

**With substitution directives**

.. code-block:: lua

  -- WITH SUBSTITUTION DIRECTIVES
  local wowVersion = "retail"
  --[===[@non-retail@
  local wowVersion = "classic"
  --@end-non-retail@]===]
  print("Hi, I'm running on " .. wowVersion .. " WoW!")

The above code will built differently for retail and classic builds. This makes it easy
to introduce bugs because developers have to keep in mind how the code differs in each
case. It is no longer Lua code -- it is an overloading of Lua comments into a
preprocessing language with its own esoteric syntax and keyword names.

Additionally, you can't run static analyzers like
`luacheck <https://github.com/mpeterv/luacheck>`_ on this code.

**With pure lua code and the WoW API**

.. code-block:: lua

  -- WITH THE WOW API
  local wowVersion = "retail"
  if WOW_PROJECT_ID == WOW_PROJECT_CLASSIC then
    wowVersion = "classic"
  end
  print("Hi, I'm running on " .. wowVersion .. " WoW!")

This code is clear in its intentions. It's simply Lua code, and it leverages the WoW
API we have at hand to do the job. And, it can be statically analyzed.

And this is just the Lua. Substitution directives also exist for TOC and XML files:

- The main case for substitution in TOC files is to handle the ``Interface`` tag, which
  *wap* can do for you.
- For XML, there may be a valid use case. But, there's almost no reason to be writing
  XML. Lua can do everything that WoW XML can.

In closing, the main point is here is that there are programmatic ways to do everything
substitution directives do in your Lua code, but in a better way. And TOC file
generation is handled by *wap* itself.

Why generate TOC files?
***********************

There are two main reasons:

- Cut down on duplication. If you need to upload a retail AND a classic version, you'd
  otherwise need to create 2 nearly identical TOC files that only differ in their
  ``Interface`` tags.

  So instead, by centralizing TOC contents into the ``.wap.yml``, *wap* can generate
  your TOC file with your tags and files AND the correct ``Interface`` for the version
  of WoW you are targeting.

- TOC validation. *wap* validates that:

  * Any files listed actually exist within that folder
  * Any custom tags are prefixed with ``X-``, which is necessary for them to be
    retrievable by
    `GetAddOnMetadata <https://wowwiki-archive.fandom.com/wiki/API_GetAddOnMetadata>`_.


Why not automatically get my addon's version number from my VCS?
****************************************************************

In the spirit of keeping *wap* (and addon development in general!) accessible, I don't
want to force your hand on your addon's development process and tooling.

Besides, if you insist, you can extract a version from your VCS and use it as the
argument to any *wap* commands that accept it.

Why not support pulling in dependencies (``externals``) from other repositories?
********************************************************************************

For a variety of reasons:

- Source code repositories are not releases. That is not their purpose. Source code
  repositories are filled with all sorts of things like READMEs and ``.gitignore`` files
  and tests and documentation and the list the goes on and on... And none of that has to
  do with the Lua code that you're really after.

  That Lua code belongs in a deliberate release asset (file/zip/etc) by the project
  owner, cleansed and packaged in a way you can include in your addon.

- Even if you do have dependency repository that's tolerably clean and packaged in its
  natural form, that repository is actually a development-time dependency, not a
  release-time dependency like other addon packagers imply. It needs to be *inside* your
  environment while you write your code. Otherwise, you're coding on hope.

  * Other addon packagers don't even require a commit hash/tag to be specified, so you
    can't even be sure what of what code will be included with your addon in those
    cases. Dependencies shouldn't be changing *at all* unless you've deliberately
    upgraded them.

- It slows down your release process to redownload dependencies. Pulling them into
  source code once is much faster.

- Finally, this is just feature bloat for *wap*. It's excessive to write a ``git clone``
  and/or ``svn checkout`` runner when you can run those tools better yourself. It opens
  up a huge surface area of support if *wap* would need to be able to run those tools
  itself.

TLDR: *wap* could, but it won't. **Copy your dependencies into your project from an
official release of that dependency, or from the its repository if that is all they
offer.**

Why not upload WoWInterface too?
********************************

The momentum of the WoW community points towards CurseForge.

I actually have written WoWInterface support, but removed it because I don't think many
users would want it.

If I'm wrong about that, please create an issue and we can discuss and reassess.

Why not upload GitHub Release assets?
*************************************

- It requires that a tag is exists in the repository, which is a prerequisite for a
  GitHub release. I don't want to force your hand on your development process.

- It adds the GitHub API itself as a dependency, which is a moving target.

- It's something that other tools already do better.

Instead, I kindly suggest you incorporate something like
`Github CLI <https://cli.github.com/>` or
`upload-release-asset <https://github.com/actions/upload-release-asset>`_ into your
build process in conjunction with *wap* if you want this feature. For *wap*, it's too
much bloat for too little gain.

Contributing
------------

See `CONTRIBUTING.rst <docs/CONTRIBUTING.rst>`_.

TODOs
-----

- localization via curseforge?
- Dockerfile
- Dockerfile github action `<https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action>`_
