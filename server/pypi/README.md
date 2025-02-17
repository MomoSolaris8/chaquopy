# Introduction

This directory contains the build-wheel tool, which produces Android .whl files for Chaquopy.
build-wheel itself is only supported on Linux x86-64. However, the resulting .whls can be built
into an app on any supported Android build platform, as described in the [Chaquopy
documentation](https://chaquo.com/chaquopy/doc/current/android.html#requirements).

Install the requirements in `requirements.txt`, then run `build-wheel.py --help` for more
information.


# Adding a new package

Create a recipe directory in `packages`. Its name must be in PyPI normalized form (PEP 503).
Alternatively, you can create this directory somewhere else, and pass its path when calling
`build-wheel.py`.

Inside the recipe directory, add the following files.

* A `meta.yaml` file. This supports a subset of Conda syntax, defined in `meta-schema.yaml`.
* A `test.py` file (or `test` package), to run on a target installation. This should contain a
  unittest.TestCase subclass which imports the package and does some basic checks.
* For non-Python packages, a `build.sh` script. See `build-wheel.py` for environment variables
  which are passed to it.

Run `build-wheel.py` for x86_64. If any changes are needed to make the build work, edit the
package source code in the `build` subdirectory, and re-run `build-wheel.py` with the
`--no-unpack` option. Then copy the resulting wheel from `dist` to a private package repository
(edit `--extra-index-url` in `pkgtest/app/build.gradle` if necessary).

Temporarily add the new package to `pkgtest/app/build.gradle`, and set `abiFilters` to
x86_64 only.

Unless the package depends on changes in the development version, edit `pkgtest/build.gradle`
to use the current stable Chaquopy version. Then run the tests.

If this is a new version of an existing package, we should check that it won't break any
existing apps with unpinned version numbers. So temporarily edit `pkgtest/build.gradle` to
use the oldest Chaquopy version which supported this package with this Python version. If
necessary, also downgrade the Android Gradle plugin, and Gradle itself. Then run the tests.

If any changes are needed to make the tests work, increment the build number in `meta.yaml`
before re-running `build-wheel.py` as above.

Once the package itself is working, also test any packages that list it as a requirement in
meta.yaml, since these usually indicate a dependency on native interfaces which may be less
stable. Include these packages in all the remaining tests.

Once everything's working on x86_64, save any edits in the package's `patches` directory,
then run `build-wheel.py` for all other ABIs, and copy their wheels to the private package
repository.

Restore `abiFilters` to include all ABIs. Then test the app with the same Chaquopy versions
used above, on the following devices, with at least one device being a clean install:

* x86 emulator with minSdkVersion, or API 18 if "too many libraries" error occurs (#5316)
* x86_64 emulator with targetSdkVersion
* x86_64 emulator with API 21 (or 23 before Chaquopy 7.0.3)
* Any armeabi-v7a device
* Any arm64-v8a device

Move the wheels to the public package repository.

Update any GitHub issues, and notify any affected users who contacted us outside of GitHub.
