#!/usr/bin/env python3
"""build, sign, notarise and publish an arm64 release of the workflow."""

import argparse
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
BINARY = "alfred-firefox"
NOTARY_PROFILE = "notarytool"
ASSETS = [
    "info.plist",
    "*.png",
    "scripts/*",
    "icons/*.png",
    "LICENCE.txt",
    "README.md",
    "server.sh",
]


class ReleaseError(Exception):
    pass


def run(args: list[str], *, check=True, capture=False, **kwargs):
    result = subprocess.run(
        args,
        cwd=kwargs.pop("cwd", ROOT),
        text=True,
        capture_output=capture,
        **kwargs,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or "").strip() if capture else ""
        raise ReleaseError(f"command failed: {' '.join(args)}\n{detail}".rstrip())
    return result


def output(args: list[str]):
    return run(args, capture=True).stdout.strip()


def preflight(tag, force):
    print("checking repository state ...")
    if not force and output(["git", "status", "--porcelain"]):
        raise ReleaseError("working tree has uncommitted changes")
    run(["git", "fetch", "--quiet", "origin"])
    if not output(["git", "branch", "--remotes", "--contains", "HEAD"]):
        raise ReleaseError("HEAD has not been pushed to origin")
    tag_check = run(
        ["git", "ls-remote"]
        + ["--exit-code"]
        + ["--tags", "origin"]
        + [f"refs/tags/{tag}"],
        check=False,
        capture=True,
    )
    if tag_check.returncode == 0:
        raise ReleaseError(f"tag {tag} already exists on origin")
    return output(["git", "rev-parse", "HEAD"])


def signing_identity():
    listing = output(["security", "find-identity", "-v", "-p", "codesigning"])
    identities = sorted(
        set(re.findall(r'"(Developer ID Application: [^"]+)"', listing))
    )
    if len(identities) != 1:
        found = ", ".join(identities) or "none"
        raise ReleaseError(
            f"expected exactly one Developer ID Application identity, found: {found}"
        )
    return identities[0]


def build(binary):
    print("building arm64 executable ...")
    env = {
        **os.environ,
        "GOOS": "darwin",
        "GOARCH": "arm64",
        "CGO_ENABLED": "0",
    }
    run(
        ["go", "build", "-trimpath", "-o", str(binary), "."],
        env=env,
    )


def sign(binary, identity):
    print(f"signing with {identity} ...")
    run(
        ["codesign", "--force", "--timestamp"]
        + ["--options", "runtime"]
        + ["--sign", identity]
        + [str(binary)],
    )
    run(["codesign", "--verify", "--strict", "--verbose=2", str(binary)])


def notarise(binary, work):
    print("submitting for notarisation (this can take a few minutes) ...")
    archive = work / f"{binary.name}.zip"
    run(["ditto", "-c", "-k", "--keepParent", str(binary), str(archive)])
    result = run(
        ["xcrun", "notarytool"]
        + ["submit", str(archive)]
        + ["--keychain-profile", NOTARY_PROFILE]
        + ["--wait"]
        + ["--output-format", "json"],
        check=False,
        capture=True,
    )
    try:
        info = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise ReleaseError(f"notarytool failed:\n{result.stderr.strip()}")
    if info.get("status") != "Accepted":
        raise ReleaseError(
            f"notarisation {info.get('status', 'failed')}: {info.get('message', '')}\n"
            f"see: xcrun notarytool log {info.get('id')} --keychain-profile {NOTARY_PROFILE}"
        )
    print(f"notarisation accepted ({info.get('id')})")


def read_plist(path):
    with path.open("rb") as f:
        return plistlib.load(f)


def asset_path(version):
    name = read_plist(ROOT / "info.plist")["name"]
    asset = DIST / f"{name.replace(' ', '-')}-{version}.alfredworkflow"
    if asset.exists():
        raise ReleaseError(f"{asset.relative_to(ROOT)} already exists")
    return asset


def assemble(bundle, binary, version):
    print("assembling workflow ...")
    for pattern in ASSETS:
        for src in sorted(ROOT.glob(pattern)):
            if not src.is_file():
                continue
            dest = bundle / src.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    shutil.copy2(binary, bundle / BINARY)

    plist_path = bundle / "info.plist"
    plist = read_plist(plist_path)
    plist["version"] = version
    with plist_path.open("wb") as f:
        plistlib.dump(plist, f, sort_keys=False)


def package(bundle, asset):
    DIST.mkdir(exist_ok=True)
    run(["zip", "--quiet", "--recurse-paths", str(asset), "."], cwd=bundle)
    print(f"wrote {asset.relative_to(ROOT)}")


def publish(tag, asset, sha):
    print(f"creating release {tag} ...")
    run(
        ["gh", "release", "create"]
        + [tag, str(asset)]
        + ["--target", sha]
        + ["--title", tag]
        + ["--generate-notes"],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="version to release, e.g. 0.2.3")
    parser.add_argument(
        "--no-release",
        action="store_true",
        help="build, sign, notarise and package, but don't create the github release",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="allow releasing with uncommitted changes in the working tree",
    )
    args = parser.parse_args()

    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        parser.error(f"version must be in the form X.Y.Z, got {args.version!r}")
    tag = f"v{args.version}"

    try:
        sha = preflight(tag, args.force)
        asset = asset_path(args.version)
        identity = signing_identity()
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            binary = work / BINARY
            bundle = work / "bundle"
            bundle.mkdir()
            build(binary)
            sign(binary, identity)
            notarise(binary, work)
            assemble(bundle, binary, args.version)
            package(bundle, asset)
        if args.no_release:
            print("skipping github release")
        else:
            publish(tag, asset, sha)
    except ReleaseError as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
