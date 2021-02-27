Recommended Project Structure
=============================

The recommended project structure for ``wap`` is inspired by conventions for projects
from many other types of software. It is:

- A project root directory

  * Addon directories

    + Lua code

    + Other resources your addon needs

    + Subdirectories that contain any of the above items

  * Any number of other files and directories related to how you develop your project.

Let's take a look at an example:

.. code-block:: text

   MyProject
   ├── .github
   |   ├── CONTRIBUTING.md
   |   └── workflows
   |       └── ci.yml
   ├── MyDir
   |   ├── Init.lua
   |   ├── Core.lua
   |   └── Options.lua
   ├── AnotherDir
   |   ├── Init.lua
   |   ├── Font.ttf
   |   ├── AlertSound.mp3
   |   └── Tooltip.lua
   ├── CHANGELOG.md
   ├── README.md
   ├── LICENSE
   ├── .luacheckrc
   ├── .gitignore
   └── .wap.yml

.. note::

   Again, this is just an example. Do not try to create each file that appears here in
   your project. This is just to illustrate structure and semantics. Use the
   :ref:`wap-quickstart` command if you want to create a project that follows these
   principles.

At the root is your project directory (``MyProject``). This contains everything related
to your project: source code, documentation, and configuration. If you are using
version control, this would the the ideal location of your repository.

Inside your project directory, there are source code directories (``MyDir`` and
``AnotherDir``). The fact that these are directories and not straight Lua files is a
consequence of how World of Warcraft expects addons to be: a directory (or several)
that contains Lua code and/or other resources that your addon uses.

Also note the documentation files, configuration files, and other project metadata.
These are things that you want to include when developers work on your project, but
should not in your packaged addon. Therefore, they live at the project root level.

Version Control Suggestions
---------------------------

- Again, set the repository to be at the root level of your project.
- You should definitely check in the ``.wap.yml`` file
- You should add the ``dist/`` directory to your ``.gitignore`` file. Any builds of
  your addon are derived from the source files. So, you can always recreate builds and
  don't need to keep them around.
