#!/usr/bin/env python3
"""Patch the generated openapi-python-client package with correct metadata.

After openapi-python-client generates the client, this script updates the
pyproject.toml with the correct package name, version, description, and
other metadata needed for PyPI publishing.
"""

import argparse
import sys
from pathlib import Path


PYPROJECT_TEMPLATE = """\
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "tandoor-client"
version = "{version}"
description = "Auto-generated Python client for the Tandoor Recipes API"
readme = "README.md"
license = "MIT"
requires-python = ">=3.12"
authors = [
    {{name = "Tandoor Client Auto-Publisher"}},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Typing :: Typed",
]
keywords = ["tandoor", "recipes", "api", "client", "openapi"]
dependencies = [
    "httpx>=0.20.0",
    "attrs>=21.3.0",
    "python-dateutil>=2.8.0",
]

[project.urls]
Homepage = "{repo_url}"
"Tandoor Recipes" = "{upstream_url}"
"Bug Tracker" = "{repo_url}/issues"

[tool.setuptools.packages.find]
include = ["tandoor_client*"]
"""


def patch_pyproject(package_dir: Path, version: str, repo_url: str,
                    upstream_url: str) -> None:
    """Replace the generated pyproject.toml with our metadata."""
    pyproject_path = package_dir / "pyproject.toml"

    content = PYPROJECT_TEMPLATE.format(version=version, repo_url=repo_url,
                                        upstream_url=upstream_url)
    pyproject_path.write_text(content)
    print(f"Patched {pyproject_path} with version {version}")


def create_package_readme(package_dir: Path, version: str, repo_url: str) -> None:
    """Create a minimal README for the generated package."""
    readme_path = package_dir / "README.md"
    readme_path.write_text(
        f"# tandoor-client v{version}\n\n"
        "Auto-generated Python client for the [Tandoor Recipes](https://tandoor.dev) API.\n\n"
        "## Installation\n\n"
        "```bash\n"
        "pip install tandoor-client\n"
        "```\n\n"
        "## Usage\n\n"
        "```python\n"
        "from tandoor_client import Client\n\n"
        'client = Client(base_url="https://your-tandoor-instance.com")\n'
        "```\n\n"
        f"See the [main repository]({repo_url}) for more details.\n"
    )
    print(f"Created {readme_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Patch generated client package metadata")
    parser.add_argument("package_dir", type=Path, help="Path to the generated package directory")
    parser.add_argument("version", help="Package version string")
    parser.add_argument("--repo-url", required=True, help="Publisher repository URL")
    parser.add_argument("--upstream-url", required=True, help="Upstream project URL")
    args = parser.parse_args()

    if not args.package_dir.is_dir():
        print(f"Error: package directory {args.package_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    patch_pyproject(args.package_dir, args.version, args.repo_url, args.upstream_url)
    create_package_readme(args.package_dir, args.version, args.repo_url)


if __name__ == "__main__":
    main()
