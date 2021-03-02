Some Essential Terminology
==========================

When using ``wap`` (and reading this documentation), you'll encounter some terms that
require explicit definition.

addon
  A directory filled with a TOC, Lua, XML, and other resource files (like
  fonts or sounds). Installed in a user's AddOns directory, these files
  perform some function within World of Warcraft.

  .. code-block::

     addon
     ├── TOC file
     ├── Lua files
     ├── XML documents
     ├── Textures/Fonts/Sounds/etc
     └── Subdirectories of any of the above

  Addons, however, may be dependent on or dependencies of other addons. When you have
  two or more addons in your project have this kind of relationship, you need a
  higher-level concept to describe them as a set: a **package**.

package
  A set of addons from a project. This is the distributable asset that represents a
  release.

  When packaged, a package is either single directory containing all the addons or
  a ZIP file containing all the addons at the root.

  The ZIP file is what you upload to CurseForge, and subsequently, what users get when
  they download your file.

  ``wap`` **commands operate on the package level, not the addon level**.

  .. code-block::

     package
     ├── addon
     ├── addon
     └── ...

  .. note::

     Most packages will only contain one addon.

     Some authors will chose to create several different addons in their package because
     they need to leverage different types of `conditional loading`_ or other advanced
     features.


.. _`conditional loading`: https://wow.gamepedia.com/TOC_format#Loading_conditions
