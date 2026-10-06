#!/usr/bin/env python3
"""Update the XFER formula from the latest GitHub release metadata."""

import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

FORMULA = Path(__file__).resolve().parents[1] / "Formula" / "xfer.rb"
API = "https://api.github.com/repos/cdenihan/XFER/releases/latest"
PLATFORM_ASSETS = {"arm": "aarch64", "intel": "x86_64"}


def main() -> None:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "cdenihan-homebrew-tap"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(API, headers=headers), timeout=30) as response:
        release = json.load(response)

    tag = release["tag_name"]
    if not re.fullmatch(r"v[0-9]+(?:\.[0-9]+){2,3}", tag):
        raise ValueError(f"Unexpected release tag: {tag!r}")
    version = tag.removeprefix("v")

    digests = {}
    release_assets = release["assets"]

    version_asset_matches = [asset for asset in release_assets if asset["name"] == "VERSION"]
    if len(version_asset_matches) != 1:
        raise ValueError(f"Expected one VERSION asset in {tag}, found {len(version_asset_matches)}")
    version_asset = version_asset_matches[0]
    expected_url = f"https://github.com/cdenihan/XFER/releases/download/{tag}/VERSION"
    if version_asset["browser_download_url"] != expected_url:
        raise ValueError("Unexpected VERSION download URL")
    digest = version_asset.get("digest", "")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError(f"Missing or invalid SHA-256 digest for VERSION in {tag}")
    digests["VERSION"] = digest.removeprefix("sha256:")

    asset_names = {"VERSION": "VERSION"}
    for platform, arch in PLATFORM_ASSETS.items():
        preferred_name = f"xfer-{version}-{arch}-macos.tar.gz"
        fallback_name = f"xfer-macos-{arch}"
        matches = [asset for asset in release_assets if asset["name"] in {preferred_name, fallback_name}]
        if len(matches) != 1:
            raise ValueError(
                f"Expected one macOS {arch} asset in {tag}, found {len(matches)}"
            )
        asset = matches[0]
        name = asset["name"]
        expected_url = f"https://github.com/cdenihan/XFER/releases/download/{tag}/{name}"
        if asset["browser_download_url"] != expected_url:
            raise ValueError(f"Unexpected {name} download URL")
        digest = asset.get("digest", "")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError(f"Missing or invalid SHA-256 digest for {name} in {tag}")
        digests[platform] = digest.removeprefix("sha256:")
        asset_names[platform] = name

    formula = FORMULA.read_text()
    current_tags = {}
    current_digests = {}
    current_asset_names = {}

    version_matches = list(
        re.finditer(
            r'(?m)^  url "https://github.com/cdenihan/XFER/releases/download/(v[0-9.]+)/VERSION"\n'
            r'  sha256 "([0-9a-f]{64})"$',
            formula,
        )
    )
    if len(version_matches) != 1:
        raise ValueError("Cannot locate exactly one VERSION URL and checksum in the formula")
    current_tags["VERSION"], current_digests["VERSION"] = version_matches[0].groups()
    current_asset_names["VERSION"] = "VERSION"

    for platform, block in (("arm", "on_arm"), ("intel", "on_intel")):
        matches = list(
            re.finditer(
                rf'(?m)^    {block} do\n'
                r'      url "https://github.com/cdenihan/XFER/releases/download/(v[0-9.]+)/([^/"]+)"\n'
                r'      sha256 "([0-9a-f]{64})"$',
                formula,
            )
        )
        if len(matches) != 1:
            raise ValueError(f"Cannot locate exactly one {platform} URL and checksum in the formula")
        current_tags[platform], current_asset_names[platform], current_digests[platform] = matches[0].groups()
    if len(set(current_tags.values())) != 1:
        raise ValueError("Formula assets use different release tags")

    current = current_tags["VERSION"]
    old_version = tuple(map(int, current[1:].split(".")))
    new_version = tuple(map(int, tag[1:].split(".")))
    if len(new_version) == len(old_version) and new_version < old_version:
        raise ValueError(f"Latest release {tag} is older than formula release {current}")
    if new_version == old_version:
        if current_digests != digests:
            raise ValueError(f"Checksum changed for existing release {tag}")
        print(f"Already at {tag}")
        return

    for name in ("VERSION", "arm", "intel"):
        old_url = (
            f"https://github.com/cdenihan/XFER/releases/download/"
            f"{current}/{current_asset_names[name]}"
        )
        new_url = f"https://github.com/cdenihan/XFER/releases/download/{tag}/{asset_names[name]}"
        formula = formula.replace(old_url, new_url, 1)
        formula = formula.replace(f'sha256 "{current_digests[name]}"', f'sha256 "{digests[name]}"', 1)
    FORMULA.write_text(formula)
    print(f"Updated XFER from {current} to {tag}")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError) as exc:
        print(f"XFER update failed: {exc}", file=sys.stderr)
        sys.exit(1)
