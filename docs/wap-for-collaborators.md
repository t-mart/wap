# wap for Collaborators

If you're collaborating on an project that uses `wap`, do the following to get started:

1. First, [install `wap`](installation.md).

2. If you haven't already, fork or clone the project that you want to work on. For example:

    ```shell
    git clone https://github.com/t-mart/ItemVersion.git
    ```

3. Navigate to the project's root directory. For example:

    ```shell
    cd ItemVersion
    ```

4. [Build](commands/build.md) the project:

    ```shell
    wap build
    ```

    Then, look in the `dist/` directory for the built addon package.

    At this point, you could copy-paste that directory into your WoW `Interface/AddOns` directory,
    but `wap` has a much more elegant developer-experience solution: run `wap build` in
    [`--watch`](commands/build.md#-watch) and [`--link`](commands/build.md#-link) mode to have
    it automatically rebuild and link into your AddOns directory. No copy-pasting needed!

    ```shell
    wap build --watch --link
    ```

5. Run the game, and see the addon in action. Make any changes you'd like, and see them reflected
   after reloading the client. (One way to reload is to type `/reload` in the chat window.)
