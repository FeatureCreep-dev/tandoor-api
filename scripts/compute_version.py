#!/usr/bin/env python3
"""Compute PEP 440 version string for tandoor-client from an upstream tag.

Normalizes upstream tags to three-component semver (e.g., '2.5' -> '2.5.0').
Tracks the last-published ref in upstream_state.json.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def get_latest_upstream_tag(upstream_url: str) -> str:
    """Query upstream repo for the latest semver tag."""
    result = subprocess.run(
        ["git", "ls-remote", "--tags", "--sort=-v:refname", upstream_url],
        capture_output=True, text=True, check=True,
    )

    tags = []
    for line in result.stdout.strip().splitlines():
        ref = line.split("\t")[1] if "\t" in line else ""
        if ref.endswith("^{}"):
            continue
        tag = ref.replace("refs/tags/", "")
        if re.match(r"^\d+\.\d+(\.\d+)?$", tag):
            tags.append(tag)

    if not tags:
        return "0.0.0"

    def sort_key(t: str) -> tuple:
        parts = t.split(".")
        return tuple(int(p) for p in parts)

    tags.sort(key=sort_key, reverse=True)
    return tags[0]


def normalize_tag(tag: str) -> str:
    """Ensure tag has three components (e.g., '2.5' -> '2.5.0')."""
    parts = tag.split(".")
    while len(parts) < 3:
        parts.append("0")
    return ".".join(parts[:3])


def compute_version(state_file: Path, upstream_url: str,
                    tag_override: str | None = None) -> str:
    """Compute the PEP 440 version from the upstream tag."""
    if tag_override:
        return normalize_tag(tag_override)
    return normalize_tag(get_latest_upstream_tag(upstream_url))


def update_state(state_file: Path, ref: str, tag: str) -> None:
    """Update upstream_state.json with the new ref and tag."""
    state = json.loads(state_file.read_text())
    state["last_ref"] = ref
    state["last_tag"] = tag
    state_file.write_text(json.dumps(state, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute version for tandoor-client")
    parser.add_argument("--state-file", type=Path, default=Path("upstream_state.json"))
    parser.add_argument("--upstream-url", required=True, help="Upstream git repository URL")
    parser.add_argument("--tag", help="Tag override (use this instead of querying upstream)")
    parser.add_argument("--update-ref", help="Update state with this ref after computing version")
    args = parser.parse_args()

    version = compute_version(args.state_file, args.upstream_url, args.tag)
    print(version)

    if args.update_ref:
        update_state(args.state_file, args.update_ref, args.tag or version)


if __name__ == "__main__":
    main()
