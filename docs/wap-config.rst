The ``wap`` Configuration File
------------------------------

``wap`` only needs one file to operate: a YAML file named ``.wap.yml``.

This file should be placed at the root of your project directory.

For new YAML authors, see `What is YAML?`_.

.. warning::
  For advanced YAML authors, it may be important to note that ``wap`` uses a subset of
  YAML called `strictyaml`_. This provides many benefits for users, but does
  `restrict some buggy YAML features`_. There's a good chance you won't even notice a difference.

.. warning::
  In ``wap`` configuration files, all paths are treated as POSIX paths. The main takeaway
  of this is that path separators (the slashes between directories and subdirectories
  and files) are **forward slashes** (``/``). By choosing a standard, configuration
  files become cross-platform, so developers on any other system can contribute to your
  project.

  .. code-block:: yaml

     path/to/my.lua    # GOOD, only forward slashes
     path\to\my.lua    # bad, uses backslashes
     path/to\my.lua    # bad, uses mixed slashes

Sample Config File and Directory Structure
******************************************

Here's a commented sample ``.wap.yml`` file:

.. code-block:: yaml

  # the name of your addon, can be anything you like
  name: MyAddon

  # a list of versions of WoW your addon works on
  wow-versions:
    - 9.0.2
    - 1.13.6

  # if you want to upload to CurseForge, include this section
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

**Required**. The name of your packaged addon. This name will be used to name the build directories
and zip files for your addon (as well as the zip file users download on CurseForge).

You can name this anything you want.

Example:

.. code-block:: yaml

  name: MyAwesomeAddon

``wow-versions``
^^^^^^^^^^^^^^^^

**Required**. A ``list`` of the versions of World of Warcraft that your addon supports.
``wap`` will create different builds for each version in the output directory.

Each version must be in the form ``x.y.z``, where ``x``, ``y``, and ``z`` are
non-negative integers.

You must at least supply one of these, and can at most supply two (for retail and
classic).

``wap`` uses these versions for a few things:

- To properly generate your TOC file with the right ``## Interface`` tag
- To mark on CurseForge which version your addon supports
- To ``dev-install`` the right build into the right WoW AddOns path. For example a
  classic addon build should not go into a
  ``World of Warcraft/_retail_/Interface/AddOns`` directory.

Examples:

.. code-block:: yaml

  # just retail
  wow-versions:
    - 9.0.2

.. code-block:: yaml

  # just classic
  wow-versions:
    - 1.13.6

.. code-block:: yaml

  # retail and classic
  wow-versions:
    - 9.0.2
    - 1.13.6

.. warning::
  You do need to ensure these versions are actaully valid WoW versions, or else your
  upload to CurseForge will fail.

  One surefire way of getting a valid version is looking at the Battle.net Launcher
  and looking at the first 3 digits of the version list there:

  .. image:: _static/valid-wow-version.png
     :alt: A version in the Battle.net Launcher

``curseforge``
^^^^^^^^^^^^^^

A ``map`` of configuration options for CurseForge. If you want to upload your project to
CurseForge, you must include this section.

``curseforge.project-id``
^^^^^^^^^^^^^^^^^^^^^^^^^

**Required**. The project id as found on your CurseForge addon's page. This field tells wap
what addon page to upload to.

.. image:: _static/where-to-find-project-id.png
  :alt: Where to find your CurseForge project id


Example:

.. code-block:: yaml

  curseforge:
    project-id: 433258
    # ...

``curseforge.changelog-file``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The path, relative the project root directory, of your changelog file. This file should
contain a helpful history of changes to your addon over time. There are no
requirements for the contents of this file -- it just needs to exist. You may leave
it blank if you're just starting out.

.. note::
  This field is optional. But if you do not provide it, you must use the
  ``--changelog-contents`` and ``--changelog-type`` options when you run the upload
  command: Curseforge requires this data. It accompanies each file uploaded to the site.

  CurseForge aside, maintaining a changelog file is a good practice. This is helpful
  information for both your users and collaborators.

See the `Sample Config File and Directory Structure`_ section for an example on where
this file is expected to be inside your project.

The CurseForge API also requires a changelog type, which indicates the format of your
log contents. They support the following three:

- ``markdown``
- ``html``
- ``text``

``wap`` will try to chose the correct format based on the extension of the file you
provide for this field. It does so according to the following mapping:

+-----------------+-------------------+
| File Extension  | Changelog Type    |
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

Example:

If you had a project structure like this:

.. code-block::

   MyProject
   ├── MyDir
   ├── CHANGELOG.md
   └── .wap.yml

then you would fill in this field like this:

.. code-block:: yaml

  curseforge:
    changelog-file: CHANGELOG.md
    # ...


``curseforge.project-slug``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Required**. The string of the name of your addon as it is found in your addon's CurseForge
URL.

While not strictly necessary, this helps ``wap`` provide better output for you in the
form of URLs that you can copy-paste into your browser after you upload.

Example:

If your addon's URL is ``https://www.curseforge.com/wow/addons/mycooladdon``, then you
would fill in this field like this:

.. code-block:: yaml

  curseforge:
    project-slug: mycooladdon
    # ...

``dirs``
^^^^^^^^

**Required**. A list of directories to include in your packaged addon.

Many small addons will only contain a single ``dirs`` item, but more complex ones
will have many.

``dirs[*].path``
^^^^^^^^^^^^^^^^

**Required**. The path, relative to the project root directory, of the directory you'd
like to include in your packaged addon.

This cannot be a file -- it must be a directory because only directories are installable
into WoW addons folders.

Example:

If you had a project structure like this:

.. code-block::

   MyProject
   ├── MyDir
   ├── MyOtherDir
   └── .wap.yml

then you would fill in this field like this:

.. code-block:: yaml

  dirs:
    - path: MyDir
    # ...
    - path: MyOtherDir
    # ...

``dirs[*].toc``
^^^^^^^^^^^^^^^

**Required**. The configuration for this directory's generated TOC file. The generated
TOC file will have the same name as the directory (plus the ``.toc`` extension) and be
placed at the root of that directory.

For more information on why TOC file generation is a good thing, see
`Why generate TOC files?`_.

``dirs[*].toc.tags``
^^^^^^^^^^^^^^^^^^^^

**Required**. A ``map`` of key-value pairs to include in the generated TOC file. The keys and values
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
  **You should not provide the** ``Interface`` **and** ``Version`` **tags!** ``wap`` generates
  those tags for you. You can override them, but it is not recommended.

``dirs[*].toc.files``
^^^^^^^^^^^^^^^^^^^^^

**Required**. A sequence of paths, relative to the ``path`` of the item in ``dirs``, that specify
the Lua (or XML) files
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
not exist almost certainly indicate an bug, so ``wap`` will abort if such a case is
found and print the missing file.

.. _`strictyaml`: https://hitchdev.com/strictyaml/
.. _`What is YAML?`:  https://blog.stackpath.com/yaml/
.. _`restrict some buggy YAML features`: https://hitchdev.com/strictyaml/#design-justifications