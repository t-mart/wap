Why ...?
========

Why make another addon tool?
****************************

``wap`` is a reimagining of how developers create addons. The most popular current
solution is probably the `packager`_ project,
and I think there are things that could be improved about it. Namely, it:

- Encourages the use :ref:`substitution directives <why-not-substitution-directives>` (e.g. ``--@keyword@``)
- Conflates :ref:`dependencies and source code repositories <why-not-externals>`. They are not
  the same thing.
- Presumes your entire repository should be packaged up, which is awkward and
  heavy-handed for most modern projects and requires ``ignore``-ing many files.
- Mandates the use of :ref:`certain version control processes <why-not-get-version-from-vcs>`,
  which are inaccessible for beginning developers.
- Reads its configuration from several files (``.pkgmeta`` and ``.toc`` files).

.. _why-not-substitution-directives:

Why not implement substitution directives like ``--@retail@``?
**************************************************************

The `packager`_ project allows you to use comments as a way to conditionally include
or exclude code in your built addons. I think this is bad. Let's compare two examples:

**With substitution directives**

.. code-block:: lua

  --[===[@retail@
  local wowVersion = "retail"
  --@end-retail@]===]
  --[===[@non-retail@
  local wowVersion = "classic"
  --@end-non-retail@]===]
  print("Hi, I'm running on " .. wowVersion .. " WoW!")

The above code will built differently for retail and classic builds. This makes it easy
to introduce bugs because developers have to keep in mind how the code differs in each
case. It is no longer Lua code -- it is an overloading of Lua comments into a
preprocessing language with its own esoteric syntax and keyword names.

And, I'd also argue its ugly. It's hard to read, write and maintain.

Sometimes too, `packager`_ can be quite slow at this step. Some of my builds
take `7+ minutes at this step`_!

Finally, you can't run static analyzers like `luacheck`_ on this code.

**With pure lua code and the WoW API**

.. code-block:: lua

  local wowVersion = "retail"
  if WOW_PROJECT_ID == WOW_PROJECT_CLASSIC then
    wowVersion = "classic"
  end
  print("Hi, I'm running on " .. wowVersion .. " WoW!")

This code is clear in its intentions. It's simply Lua code, and it leverages the WoW
API we have at hand to do the job. It's also fast to build because it has no
directives and it can be statically analyzed.

And this is just the Lua. `packager`_ has similar constructs for TOC and XML files
(albeit, in a slightly different syntax for *each language*). Here's why you wouldn't
want to use substitution directives in those cases either:

- For XML, the same comment-overloading exists. (Even so, there's almost no reason to be writing
  XML in addons these days. Lua can do everything that WoW XML can.)
- The main case for substitution in TOC files is to handle the ``Interface`` tag, which
  ``wap`` can do for you.

The main point is here is that you can do everything substitution directives can do
with Lua code, ``wap``, or a combination of the two.


.. _why-not-get-version-from-vcs:

Why not automatically get my addon's version number from my VCS?
****************************************************************

In the spirit of keeping ``wap`` (and addon development in general!) accessible, I don't
want to force your hand on your addon's development process and tooling.

Besides, if you insist, you can extract a version from your VCS and use it as the
argument to any ``wap`` commands that accept it, such as:

.. code-block:: console

  $ RELEASE_VERSION="$(git describe --always --tags --exact-match)"
  $ wap build --addon-version "$RELEASE_VERSION"
  $ wap upload --addon-version "$RELEASE_VERSION"


.. _why-not-externals:

Why not support pulling in dependencies (``externals``) from other repositories?
********************************************************************************

`packager`_ allows you to define ``externals`` in its configuration file. These
are links to source code repositories that are downloaded into your project when you
build it. This is bad for a few reasons:

- Source code repositories are not released software. That is not their purpose. Source code
  repositories are filled with all sorts of things like READMEs and ``.gitignore`` files
  and tests and documentation and the list the goes on and on... And none of that has to
  do with the Lua code that you're really after.

  That Lua code belongs in a deliberate release asset (file/zip/etc) by the project
  owner, cleansed and packaged in a way you can include in your addon.

  *(Other software systems solve this problem with package managers, but alas, there is
  none for World of Warcraft.)*

- Even if you do have dependency repository that's tolerably clean and packaged in its
  natural form, that repository is actually a development dependency, not a
  build dependency like packager implies. It needs to be *inside* your
  environment while you write your addon. Otherwise, you're coding on hope.

  * packager doesn't even require a commit hash or tag to be specified, so you
    can't even be sure what of what code will be included with your addon in those
    cases. Dependencies shouldn't be changing *at all* unless you've deliberately
    upgraded them.

- It slows down your development processes to redownload dependencies. Pulling them into
  source code once is much faster than pulling them in each time you build your addon.

- Finally, this is just feature bloat for ``wap``. It's excessive to write a ``git clone``
  and/or ``svn checkout`` runner when you can run those tools better yourself. It opens
  up a huge surface area of support if ``wap`` would need to be able to run those tools
  itself.

**TLDR:** ``wap`` **could, but it won't**. Instead, the recommended way to get
dependencies into your project is to copy your them from an official release (or from
a cloned repository if that's all that's offered) and add them to your source code.

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

Instead, I kindly suggest you incorporate something like `Github CLI`_ or
`upload-release-asset`_ into your
release process in conjunction with ``wap`` if you want this feature. For ``wap``, it's too
much bloat for too little gain.

.. _`packager`: https://github.com/BigWigsMods/packager
.. _`luacheck`: https://github.com/mpeterv/luacheck
.. _`7+ minutes at this step`: https://github.com/t-mart/ItemVersion/runs/1864902187
.. _upload-release-asset: https://github.com/actions/upload-release-asset
.. _`Github CLI`: https://cli.github.com/