#!/usr/bin/env python3
"""Update the cosmocc formula from the latest Cosmopolitan GitHub release."""

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

FORMULA = Path(__file__).resolve().parents[1] / "Formula" / "cosmocc.rb"
API = "https://api.github.com/repos/jart/cosmopolitan/releases/latest"
URL_PATTERN = re.compile(
    r'(?m)^  url "(https://github.com/jart/cosmopolitan/releases/download/'
    r'([0-9]+(?:\.[0-9]+){2})/cosmocc-\2\.zip)"\n'
    r'  sha256 "([0-9a-f]{64})"$'
)


def main() -> None:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "cdenihan-homebrew-tap"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(API, headers=headers), timeout=30) as response:
        release = json.load(response)

    version = release["tag_name"]
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){2}", version):
        raise ValueError(f"Unexpected release tag: {version!r}")

    formula = FORMULA.read_text()
    match = URL_PATTERN.search(formula)
    if not match or len(URL_PATTERN.findall(formula)) != 1:
        raise ValueError("Cannot locate exactly one cosmocc URL and checksum")
    old_url, current, old_sha = match.groups()
    if tuple(map(int, version.split("."))) < tuple(map(int, current.split("."))):
        raise ValueError(f"Latest release {version} is older than formula release {current}")
    if version == current:
        print(f"Already at {version}")
        return

    name = f"cosmocc-{version}.zip"
    assets = [asset for asset in release["assets"] if asset["name"] == name]
    if len(assets) != 1:
        raise ValueError(f"Expected one {name} asset, found {len(assets)}")
    url = f"https://github.com/jart/cosmopolitan/releases/download/{version}/{name}"
    if assets[0]["browser_download_url"] != url:
        raise ValueError(f"Unexpected {name} download URL")

    digest = assets[0].get("digest") or ""
    if re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        sha = digest.removeprefix("sha256:")
    else:
        checksum = hashlib.sha256()
        with urlopen(Request(url, headers={"User-Agent": headers["User-Agent"]}), timeout=120) as response:
            for chunk in iter(lambda: response.read(1024 * 1024), b""):
                checksum.update(chunk)
        sha = checksum.hexdigest()

    formula = formula.replace(old_url, url, 1)
    formula = formula.replace(f'sha256 "{old_sha}"', f'sha256 "{sha}"', 1)
    FORMULA.write_text(formula)
    print(f"Updated cosmocc from {current} to {version}")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError) as exc:
        print(f"cosmocc update failed: {exc}", file=sys.stderr)
        sys.exit(1)
