.. _toc-gen:

TOC File Generation
===================

One of ``wap``'s nicer features is TOC file generation. This helps you in a few ways:

- Validation. ``wap`` validates that:

  * Any files listed actually exist within that addon directory. Listing a file that does not
    exist is certainly a bug, so ``wap`` will abort with an error message.

  * Any custom tags are prefixed with ``X-``, which is necessary for them to be
    retrievable by `GetAddOnMetadata`_. ``wap`` will only warn you of this case because
    it does not break your addon.

- Cut down on duplication.

  Witout ``wap``, if you need to upload a retail *and* a classic version, you'd
  need to create two nearly identical TOC files that only differ in their ``Interface`` tags.

  Instead, by generating TOC files from configuration, ``wap`` can build those slightly
  different files for you automatically.

The TOC file is mostly generated from your :ref:`TOC configuration<config-addons-toc>`.
Additionally, ``wap`` will add some other tags:

- ``Interface``. This tag indicates which version of WoW your addon supports. The value
  comes from the :ref:`WoW version <config-wow-versions>`
  that you are building for, but is formatted slightly differently. For example,
  WoW version ``9.0.2`` would appear here as ``90002`` or ``1.13.6`` would appear here
  as ``11306``.
- ``Version``. This tag indicates the version of your package. The value here is supplied
  by you on as a command line option when you run ``wap`` commands (or, by default, is
  ``dev``).
- ``X-BuildDateTime``. This custom tag is set to the datetime of build in `ISO 8601`_ format
  in the UTC timezone.
- ``X-BuildTool``. This custom tag is set to a string like ``wap v<wap-version>``.

Example
-------

A ``.wap.yml`` configuration like this:

.. code-block:: yaml

  name: MyProject
  wow-versions:
    - 9.0.2
  addons:
    - path: MyAddon
      toc:
        tags:
          Title: MyAddon
          Notes: A great addon for WoW
          Author: Me
          X-CustomTag: CustomValue
        files:
          - Init.lua
          - Core.lua

run with a build command like this:

.. code-block:: console

   $ wap build --addon-version 1.2.3

will produce a TOC file like this at ``dist/MyAMyProjectddon-1.2.3-retail/MyAddon/MyAddon.toc``:

.. code-block:: wowtoc

   ## Interface: 90002
   ## Version: 1.2.3
   ## X-BuildDateTime: 2021-02-26T23:05:52.980024+00:00
   ## X-BuildTool: wap v0.6.0
   ## X-CustomTag: CustomValue
   ## Title: MyAddon
   ## Author: Me
   ## Notes: A great addon for WoW

   Init.lua
   Core.lua

.. _GetAddOnMetadata: https://wow.gamepedia.com/API_GetAddOnMetadata
.. _`ISO 8601`: https://en.wikipedia.org/wiki/ISO_8601
