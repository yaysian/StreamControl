# StreamControl on macOS

This fork adds native Apple Silicon and Intel build jobs for macOS 15 or newer.
The app retains its layout editor and XML/JSON output formats. Qt Script has been
replaced with Qt's JSON parser, so a separate legacy scripting package is unnecessary.

## Build from Windows using GitHub

1. Push this repository, including `.github/workflows/build-macos.yml`, to your fork.
2. Open the fork's **Actions** tab and enable workflows if GitHub asks.
3. Select **Build macOS → Run workflow → master → Run workflow**.
4. Wait for both **AppleSilicon** and **Intel** jobs to succeed. Open a failed job
   to inspect its logs; a failed build does not produce a usable application.
5. Download `StreamControl-AppleSilicon` or `StreamControl-Intel` from the run's
   **Artifacts** section. GitHub wraps the application's ZIP in another ZIP.
6. Transfer the download intact to the Mac. Extract both layers there and move
   `StreamControl.app` to Applications. Qt does not need to be installed on that Mac.

Workflows also run on pushes to master, main, and macos-build, and on pull requests.
Artifacts expire after 30 days; rerun the workflow to regenerate them.
Each job uses its native architecture and Qt 5 from Homebrew, records tool versions,
runs automated checks, bundles Qt with `macdeployqt`, and applies an ad-hoc signature.
It rejects missing Cocoa plugins, wrong architectures, and non-system dependencies
outside the application before uploading the ZIP. These are separate apps, not a
universal binary. Homebrew's Qt 5 version is not pinned; the logs record the version.
Packaging also copies Homebrew libraries that `macdeployqt` misses, removes search
paths into Homebrew, and omits Qt's unused on-screen virtual keyboard plugins.
If a job fails, its error annotations show the relevant log lines without signing in.

These personal-use builds are not Developer ID signed or notarized. macOS may
require approval in **System Settings → Privacy & Security → Open Anyway** after
the first launch attempt. Do not disable Gatekeeper globally.

## Settings and layouts

On macOS, the working directory is set to:

`~/Library/Application Support/StreamControl/`

Settings are saved as `settings.xml`. On first launch, the bundled `layout.xml`
is copied here as a writable file; existing layouts are never overwritten.
Initial output also goes here. Use Configuration to select a layout and output
directory for your overlays. Relative paths resolve from this data directory,
regardless of whether you launch from Finder or Terminal.

Existing portable settings are not automatically imported. Back them up, copy
them into this directory while the app is closed, and update any Windows paths.
Windows and Linux retain their existing working-directory behavior.

Global hotkeys are not implemented on macOS. Use the app's controls and normal
Save shortcut. XSplit/SWF playback is not included. Existing Twitter/API integrations
still require working credentials and service compatibility; the default credentials
are placeholders. This change does not modernize those services.

## Local build on a Mac

Install Xcode command-line tools and Homebrew, then:

```bash
brew install qt@5
bash scripts/build-macos.sh
```

The archive is written to `dist/`. Build directories are reusable for the same
Qt version and architecture; use a fresh checkout after changing either.

## Verification

CI tests check Unicode/XML escaping, score output in JSON and XML, restart
persistence, and macOS startup from an unrelated directory without replacing a
custom layout. These checks supplement manual testing; they do not validate Finder
launch, overlays, or online services.

Before using either build for a broadcast, test on that Mac architecture:

- Open the app from Finder with no Qt development installation present.
- Select a writable output folder, edit names/scores, and save both output formats.
- Confirm the overlay reads those outputs and updates correctly.
- Quit and reopen; verify settings and saved values remain.
- Load a custom layout, including any relative dataset paths you use.

The bundle includes the StreamControl license and installed Qt license notices.
Qt is dynamically linked. Qt source for the installed version is available from
https://download.qt.io/archive/qt/ and the Homebrew formula's referenced patches.
