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
ASSETS = ("zc.com", "zc-boot.com")


def main() -> None:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "cdenihan-homebrew-tap"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(API, headers=headers), timeout=30) as response:
        release = json.load(response)

    tag = release["tag_name"]
    if not re.fullmatch(r"v[0-9]+(?:\.[0-9]+){2}", tag):
        raise ValueError(f"Unexpected release tag: {tag!r}")

    digests = {}
    for name in ASSETS:
        matches = [asset for asset in release["assets"] if asset["name"] == name]
        if len(matches) != 1:
            raise ValueError(f"Expected one {name} asset in {tag}, found {len(matches)}")
        asset = matches[0]
        expected_url = f"https://github.com/zenc-lang/zenc/releases/download/{tag}/{name}"
        if asset["browser_download_url"] != expected_url:
            raise ValueError(f"Unexpected {name} download URL")
        digest = asset.get("digest", "")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError(f"Missing or invalid SHA-256 digest for {name} in {tag}")
        digests[name] = digest.removeprefix("sha256:")

    formula = FORMULA.read_text()
    current_tags = {}
    current_digests = {}
    for name in ASSETS:
        pattern = rf'(?m)^  *url "https://github.com/zenc-lang/zenc/releases/download/(v[0-9.]+)/{re.escape(name)}"\n  *sha256 "([0-9a-f]{{64}})"$'
        matches = list(re.finditer(pattern, formula))
        if len(matches) != 1:
            raise ValueError(f"Cannot locate exactly one {name} URL and checksum in the formula")
        current_tags[name], current_digests[name] = matches[0].groups()
    if len(set(current_tags.values())) != 1:
        raise ValueError("Formula assets use different release tags")

    current = current_tags["zc.com"]
    old_version = tuple(map(int, current[1:].split(".")))
    new_version = tuple(map(int, tag[1:].split(".")))
    if new_version < old_version:
        raise ValueError(f"Latest release {tag} is older than formula release {current}")
    if new_version == old_version:
        if current_digests != digests:
            raise ValueError(f"Checksum changed for existing release {tag}")
        print(f"Already at {tag}")
        return

    for name in ASSETS:
        old_url = f"https://github.com/zenc-lang/zenc/releases/download/{current}/{name}"
        new_url = f"https://github.com/zenc-lang/zenc/releases/download/{tag}/{name}"
        formula = formula.replace(old_url, new_url, 1)
        formula = formula.replace(f'sha256 "{current_digests[name]}"', f'sha256 "{digests[name]}"', 1)
    FORMULA.write_text(formula)
    print(f"Updated Zen C from {current} to {tag}")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError) as exc:
        print(f"Zen C update failed: {exc}", file=sys.stderr)
        sys.exit(1)
