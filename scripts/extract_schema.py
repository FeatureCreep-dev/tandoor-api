#!/usr/bin/env python3
"""Extract OpenAPI schema from Tandoor Recipes using manage.py spectacular.

Expects to run from inside a cloned upstream repo with deps installed
and a PostgreSQL database available (Django checks connectivity on startup).

Creates a stub version_info.py if missing (normally generated at build time).
"""

import os
import subprocess
import sys
from pathlib import Path


def ensure_version_info(upstream_dir: Path) -> None:
    """Create stub cookbook/version_info.py if it doesn't exist."""
    version_info = upstream_dir / "cookbook" / "version_info.py"
    if not version_info.exists():
        version_info.parent.mkdir(parents=True, exist_ok=True)
        version_info.write_text(
            '# Auto-generated stub for schema extraction\n'
            'VERSION_NUMBER = "0.0.0"\n'
            'BUILD_REF = "schema-extraction"\n'
        )
        print(f"Created stub {version_info}")


def extract_schema(upstream_dir: Path, output_file: Path) -> None:
    """Run manage.py spectacular to generate the OpenAPI schema."""
    env = os.environ.copy()

    # Ensure Django settings module is set
    env.setdefault("DJANGO_SETTINGS_MODULE", "recipes.settings")

    ensure_version_info(upstream_dir)

    cmd = [
        sys.executable, "manage.py", "spectacular",
        "--format", "openapi-json",
        "--file", str(output_file),
    ]

    print(f"Running: {' '.join(cmd)}")
    print(f"Working directory: {upstream_dir}")

    result = subprocess.run(
        cmd,
        cwd=upstream_dir,
        env=env,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"Schema extraction failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(1)

    if not output_file.exists():
        print(f"Error: expected output file {output_file} was not created", file=sys.stderr)
        sys.exit(1)

    size = output_file.stat().st_size
    print(f"Schema extracted successfully: {output_file} ({size} bytes)")


def main() -> None:
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <upstream_dir> <output_file>", file=sys.stderr)
        sys.exit(1)

    upstream_dir = Path(sys.argv[1]).resolve()
    output_file = Path(sys.argv[2]).resolve()

    if not upstream_dir.is_dir():
        print(f"Error: upstream directory {upstream_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    extract_schema(upstream_dir, output_file)


if __name__ == "__main__":
    main()
