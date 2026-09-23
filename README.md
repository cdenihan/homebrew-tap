# Homebrew tap

Custom Homebrew packages for cdenihan.

## Zen C

Install the portable compiler published by [Zen C](https://www.zenc-lang.org/):

```sh
brew install cdenihan/tap/zenc
zc --version
```

The formula installs the official release's `zc.com` as `zc` and `zc-boot.com` as `zc-boot`. The release has no `zc-init` executable. For ordinary development, use `zc build hello.zc -o hello`; Apple's Clang provides the C backend. The release binary embeds the Zen C standard library.

`zc-boot` is a separate portable hello-world bootstrap. It creates `hello.zc`, a `Makefile`, and a roughly 1.8 GB project-local `usr/` toolchain. Its bundled instructions say to run `usr/bin/make`, then `out/hello.com`. Running macOS's `make` can fail to launch its local APE compiler. The bootstrap script currently fetches `zc.com` from `OEvgeny/zc-ape` (which reports Zen C 0.1.0 in the current release) and a floating `cosmocc.zip`; these are separate from the Brew-installed Zen C version. It skips existing downloads, so `brew upgrade zenc` and rerunning `zc-boot` do not update a bootstrapped project's toolchain. For the portable example with Brew's current `zc`, run `make ZC=zc` after bootstrapping.

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
