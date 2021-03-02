Some Essential Terminology
==========================

When using ``wap`` (and reading this documentation), you'll encounter some terms that
require explicit definition.

addon
  A directory filled with a TOC, Lua, XML, and other resource files (like
  fonts or sounds). Put together and installed in a user's AddOns directory, these
  will perform some function within World of Warcraft.

package
  A built set of addons in a project. When built, they are in either in a single
  directory or archived into ZIP file.

  .. note::

     Most packages will only contain one addon.

  A package (in a zip archive) is what you upload to CurseForge, and subsequently, what
  users download when they download.

  ``wap`` commands operated on the package level, not the addon level. For single-addon
  projects, there is no difference.

