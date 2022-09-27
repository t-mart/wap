# wap

A developer-friendly World of Warcraft addon packager.

## Features

-   Builds retail, wrath, or vanilla addons (or all three!)
-   Uploads your addons to CurseForge
-   Generates valid TOC files automagically
-   Continuously rebuilds your addon during development
-   Sets up new addon projects quickly, ready to go with one command
-   Consolidates all configuration in one easy-to-edit file
-   Supports and is tested on Windows, macOS, and Linux
-   Has awesome documentation

## wap in 5 minutes

These instructions create and upload a working addon without editing a single line of code!

1. Download and install [Python 3.10](https://www.python.org/downloads/).

2. Install `wap`:

    ```console
    pip install --upgrade --user wow-addon-packager
    ```

3. Create a new a project:

    ```console
    wap new-project
    ```

    And then, answer the prompts. Don't worry too much about your answers -- you can always change
    them later in your configuration file.

4. Change to your new project's directory. For example, if you named it "MyAddon" in the last step,
   you'd type:

    ```console
    cd MyAddon
    ```

5. Build your addon package and link it to your local World of Warcraft installation:

    ```console
    wap build --link
    ```

    At this point, **you can play the game with your addon**.

6. Upload your addon to CurseForge so that others can use it:

    ```console
    wap upload --curseforge-token "<your-token>"
    ```

    You can generate a new token at Curseforge's
    [My API Tokens](https://authors.curseforge.com/account/api-tokens) page.
