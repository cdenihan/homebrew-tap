#!/usr/bin/env python3
"""Update the Zen C formula from the latest GitHub release metadata."""

import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

FORMULA = Path(__file__).resolve().parents[1] / "Formula" / "zenc.rb"
API = "https://api.github.com/repos/zenc-lang/zenc/releases/latest"


def main() -> None:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "cdenihan-homebrew-tap"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(API, headers=headers), timeout=30) as response:
        release = json.load(response)

    tag = release["tag_name"]
    if not re.fullmatch(r"v[0-9]+(?:\.[0-9]+){2}", tag):
        raise ValueError(f"Unexpected release tag: {tag!r}")
    assets = [asset for asset in release["assets"] if asset["name"] == "zc.com"]
    if len(assets) != 1:
        raise ValueError(f"Expected one zc.com asset in {tag}, found {len(assets)}")
    asset = assets[0]
    url = f"https://github.com/zenc-lang/zenc/releases/download/{tag}/zc.com"
    if asset["browser_download_url"] != url:
        raise ValueError("Unexpected zc.com download URL")
    digest = asset.get("digest", "")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError(f"Missing or invalid SHA-256 digest for {tag}")

    formula = FORMULA.read_text()
    old_tag = re.search(r'^  url "https://github.com/zenc-lang/zenc/releases/download/(v[0-9.]+)/zc.com"$', formula, re.M)
    old_sha = re.search(r'^  sha256 "([0-9a-f]{64})"$', formula, re.M)
    if not old_tag or not old_sha:
        raise ValueError("Cannot locate the current formula URL and checksum")
    current = old_tag.group(1)
    old_version = tuple(map(int, current[1:].split(".")))
    new_version = tuple(map(int, tag[1:].split(".")))
    if new_version < old_version:
        raise ValueError(f"Latest release {tag} is older than formula release {current}")
    if new_version == old_version:
        if old_sha.group(1) != digest.removeprefix("sha256:"):
            raise ValueError(f"Checksum changed for existing release {tag}")
        print(f"Already at {tag}")
        return

    formula = formula.replace(old_tag.group(0), f'  url "{url}"', 1)
    formula = re.sub(r'^  version "[0-9.]+"$', f'  version "{tag[1:]}"', formula, count=1, flags=re.M)
    formula = formula.replace(old_sha.group(0), f'  sha256 "{digest.removeprefix("sha256:")}"', 1)
    FORMULA.write_text(formula)
    print(f"Updated Zen C from {current} to {tag}")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError) as exc:
        print(f"Zen C update failed: {exc}", file=sys.stderr)
        sys.exit(1)
