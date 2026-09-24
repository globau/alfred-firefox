<div align="center">
  <img src="https://github.com/globau/alfred-firefox/blob/master/icon.png" alt="Alfred-Firefox icon" title="Alfred-Firefox icon"/>
</div>

Firefox Assistant for Alfred
============================

Search and manipulate Firefox's bookmarks, history and tabs from Alfred.

This is a fork of [Dean Jackson's original workflow][upstream], which is no longer maintained. It is maintained by [Glob][maintainer] and releases are built for Apple silicon (arm64).

![Animated demo of workflow in use][demo]

The workflow can be easily [extended with your own actions][scripts].

Installation
------------

The workflow supports Alfred 4+ and the extension works with (at least) Firefox, Firefox Nightly and Firefox Developer Edition.

1. Download and install the [latest version of the workflow][workflow].
2. Run `ffass` in Alfred and choose `Install Firefox Extension` to get [the Firefox extension][addon].

See [the setup documentation][setup] for more details.


Migrating from the original workflow
------------------------------------

This fork uses the same bundle ID and Firefox extension as Dean Jackson's original, so it installs as an update rather than alongside it.

1. Download and open the [latest version of the workflow][workflow]. Alfred will recognise it as an update to your existing Firefox Assistant; accept the update. Your settings and custom scripts are kept.
2. Keep the Firefox extension you already have installed; there is no new extension to install.
3. Run `ffass workflow:register` in Alfred (or run `ffass` and choose `Register Workflow with Browser`) and action the result, then restart Firefox (or click the extension's icon) so it reconnects to the updated workflow.

Future updates are checked against this repository, so this migration only has to be done once.


Usage
-----

The basic usage is:

- `bm <query>` — Search bookmarks
- `bml <query>` — Search bookmarklets
- `hist <query>` — Search history
- `dl [<query>]` — Search downloads
- `tab [<query>]` — Search tabs
- `ffass [<query>]` — Workflow status and links

See [the usage documentation][usage] for full details.


Integration
-----------

The workflow can be used by other workflows to retrieve the title and URL of the active Firefox tab (in lieu of AppleScript, which Firefox doesn't support). See [the integration docs][integration] for details.


Documentation
-------------

See [the full documentation][docs] for detailed info on setting up, using and customising the workflow.


Licensing & thanks
------------------

This workflow and extension are released under the [MIT licence][licence].

It is written in [Go][go] and heavily based on the [AwGo library][awgo]. The icons are based on [Font Awesome][fontawesome].


[upstream]: https://github.com/deanishe/alfred-firefox
[maintainer]: https://github.com/globau
[addon]: https://addons.mozilla.org/en-US/firefox/addon/alfred-launcher-integration/
[licence]: https://github.com/globau/alfred-firefox/blob/master/LICENCE.txt
[workflow]: https://github.com/globau/alfred-firefox/releases/latest
[demo]: https://github.com/globau/alfred-firefox/blob/master/demo.gif
[docs]: https://github.com/globau/alfred-firefox/blob/master/doc/index.md
[scripts]: https://github.com/globau/alfred-firefox/blob/master/doc/scripts.md
[integration]: https://github.com/globau/alfred-firefox/blob/master/doc/integration.md
[usage]: https://github.com/globau/alfred-firefox/blob/master/doc/usage.md
[setup]: https://github.com/globau/alfred-firefox/blob/master/doc/setup.md
[go]: https://golang.org
[awgo]: https://github.com/deanishe/awgo
[fontawesome]: https://fontawesome.com/

