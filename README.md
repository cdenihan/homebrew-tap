# Homebrew tap

Custom Homebrew packages for cdenihan.

## Zen C

Install the portable compiler published by [Zen C](https://www.zenc-lang.org/):

```sh
brew install cdenihan/tap/zenc
zc --version
```

The formula installs `zc.com` as `zc` and the upstream `zc-boot.com` bootstrap tool as `zc-boot`. The release does not contain a `zc-init` executable. Running `zc-boot` downloads additional tools, as defined by its embedded bootstrap script. A C compiler such as Apple's Clang is needed when building Zen C programs. The standard library is embedded in the release binary.

The [update workflow](.github/workflows/update-zenc.yml) checks GitHub Releases daily and on manual dispatch. When a newer stable release has `zc.com` and `zc-boot.com` assets with SHA-256 digests, it updates the formula, installs and tests it on macOS, then commits the change. A changed checksum for an existing release fails the update instead of silently replacing the binary.

## Cosmopolitan toolchain

Install [cosmocc](https://github.com/jart/cosmopolitan) to build Zen C programs as portable APE executables:

```sh
brew install cdenihan/tap/cosmocc
zc build --cc cosmocc -o hello.com hello.zc
```

The formula keeps the toolchain's bundled files together under Homebrew's `libexec` directory and exposes `cosmocc` and `cosmoc++` on `PATH`. It is a separate package because regular Zen C builds can use Apple's Clang without this large toolchain. The [cosmocc update workflow](.github/workflows/update-cosmocc.yml) checks GitHub Releases daily, verifies the release asset's SHA-256 digest or computes one from the asset, then installs and tests a new version before committing it. The installed toolchain is roughly 1.4 GB.

## XFER

Install [XFER](https://github.com/cdenihan/XFER), the direct encrypted file transfer tool:

```sh
brew install cdenihan/tap/xfer
xfer --version
```

The formula selects the matching macOS release binary for Apple Silicon or Intel. Use `brew upgrade xfer` to update it; the built-in `xfer update` command is for standalone installations. The [XFER update workflow](.github/workflows/update-xfer.yml) checks GitHub Releases daily and on manual dispatch, verifies both macOS asset digests, tests the changed formula, and commits it.
