# GitHub Action

`wap` provides a [GitHub Action](https://docs.github.com/en/actions) so you can automate the
building and publishing of you addon.

See the official documentation here:
[https://github.com/t-mart/wap-action](https://github.com/t-mart/wap-action).

!!! example

    ```yaml
    jobs:
      build-and-release:
        name: Check
        runs-on: 'ubuntu-latest'
        steps:
          # do other steps, and then...
          - name: 'wap'
            uses: 't-mart/wap-action@master'
            with:
              - release-type: 'release'
              - curseforge-token: '${{ secrets.CURSEFORGE_TOKEN }}'
    ```
