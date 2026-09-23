# Homebrew tap

Custom Homebrew packages for cdenihan.

## Zen C

Install the portable compiler published by [Zen C](https://www.zenc-lang.org/):

```sh
brew install cdenihan/tap/zenc
zc --version
```

The formula installs `zc.com` as `zc`. A C compiler such as Apple's Clang is needed when building Zen C programs. The standard library is embedded in the release binary.

The [update workflow](.github/workflows/update-zenc.yml) checks GitHub Releases daily and on manual dispatch. When a newer stable release has a `zc.com` asset with a SHA-256 digest, it updates the formula, installs and tests it on macOS, then commits the change. A changed checksum for an existing release fails the update instead of silently replacing the binary.
