# Build StreamControl for both Mac architectures from Windows

## Outcome

Use your GitHub fork to produce two downloadable apps: **Apple Silicon** and **Intel**. You manage everything from Windows; GitHub’s Mac machines compile and package the application.

This is a build-and-port process: the existing source may need compatibility fixes before either build succeeds.

## Steps

1. **Fork the repository.** Open [StreamControl](https://github.com/farpenoodle/StreamControl), click **Fork**, and enable Actions in your fork. Clone that fork to Windows to edit the source and workflow.

2. **Add `.github/workflows/build-macos.yml`.** Give it a manual **Run workflow** trigger and two independent jobs:
   - Apple Silicon: `macos-15`
   - Intel: `macos-15-intel`

   These are architecture-specific [GitHub runner labels](https://docs.github.com/en/actions/reference/runners/github-hosted-runners). Keep them explicit so a changing `macos-latest` label cannot silently change the target.

3. **Install dependencies and compile.** Each job checks out your source, installs Homebrew’s `qt@5`, and runs that installation’s `qmake` followed by `make`. Check for the project’s required Qt modules first; if Qt Script is missing, build its matching Qt 5 source for that architecture. Record dependency versions in the logs.

4. **Fix compatibility issues in your fork.** Use the Actions error logs to resolve compilation failures, then rerun. Ensure Windows-specific code is conditionally compiled. For reliable Finder launches, store settings in the user’s Application Support folder and provide a bundled default layout. Preserve existing XML/JSON output formats.

5. **Package each successful build.** Run Qt’s `macdeployqt` to bundle the required frameworks and plugins, apply ad-hoc signing after packaging changes, then archive the `.app` using macOS tools. Qt documents this packaging process in its [deployment guide](https://doc.qt.io/archives/qt-5.15/macos-deployment.html).

6. **Upload and download the results.** Publish the archives as workflow artifacts named `StreamControl-AppleSilicon` and `StreamControl-Intel`. Open **Actions → completed run → Artifacts** to download them. Transfer the archives intact and extract them on the Mac.

## Verification

- Confirm each executable and bundled library matches its intended architecture.
- Check that packaged dependencies do not point back to Homebrew directories.
- On each Mac architecture, launch from Finder without Qt installed; load a layout, change scores, save XML/JSON, and confirm settings survive restarting.
- Treat successful compilation as a milestone, not proof that the app works.

## Initial defaults

- Target macOS 15 or newer; older macOS support requires a separate compatibility decision.
- Produce personal-use builds without Developer ID signing or notarization; macOS may require explicit approval to open them.
- First deliver the core layout and file-output functionality. Completing macOS global hotkeys is a separate follow-up.
- No changes to the public output formats or overlay interfaces.
