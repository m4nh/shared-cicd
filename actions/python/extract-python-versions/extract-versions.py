#!/usr/bin/env python3
import re
import json
import sys
from pathlib import Path


PYPROJECT_FILE = "pyproject.toml"


def parse_version(version_str):
    """Parse version string to tuple of integers for comparison."""
    parts = version_str.split(".")
    return tuple(int(p) for p in parts)


def extract_python_versions(content: str):
    """Extract Python version range from pyproject.toml content."""
    # Try different quote styles and spacing
    match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        return [], None, None

    spec_str = match.group(1).strip()

    # Parse specifier string like ">=3.9,<3.12" or ">= 3.9, < 3.12"
    min_version = None
    max_version = None

    # Split by comma and parse each part
    parts = [p.strip() for p in spec_str.split(",")]

    for part in parts:
        part = part.strip()

        # Match operator and version
        m = re.match(r"([><=!]+)\s*([0-9\.]+)", part)
        if not m:
            continue

        operator = m.group(1)
        version = m.group(2)

        if operator in (">=", ">"):
            if min_version is None or parse_version(version) > parse_version(
                min_version
            ):
                min_version = version
        elif operator in ("<=", "<"):
            if max_version is None or parse_version(version) < parse_version(
                max_version
            ):
                max_version = version

    # If only min_version is specified (e.g., ">=3.10"), use that version
    if min_version and not max_version:
        print(
            f"Warning: No maximum Python version found in '{spec_str}'. Using minimum version only.",
            file=sys.stderr,
        )
        return [min_version], min_version, max_version

    if not min_version or not max_version:
        print(
            f"Warning: Could not extract min/max versions from '{spec_str}'",
            file=sys.stderr,
        )
        return [], min_version, max_version

    # Generate list of versions
    min_parts = parse_version(min_version)
    max_parts = parse_version(max_version)

    # Ensure we have at least major.minor
    while len(min_parts) < 2:
        min_parts = min_parts + (0,)
    while len(max_parts) < 2:
        max_parts = max_parts + (0,)

    versions = []

    # Handle single major version (most common case)
    if min_parts[0] == max_parts[0]:
        # Generate all minor versions from min to max (exclusive of max)
        for minor in range(min_parts[1], max_parts[1]):
            versions.append(f"{min_parts[0]}.{minor}")
    else:
        # Handle multiple major versions
        for major in range(min_parts[0], max_parts[0]):
            if major == min_parts[0]:
                # Start from min_minor
                for minor in range(min_parts[1], 20):  # Assume max 20 minor versions
                    versions.append(f"{major}.{minor}")
            else:
                # All minor versions for intermediate major versions
                for minor in range(0, 20):
                    versions.append(f"{major}.{minor}")

    return versions, min_version, max_version


def format_matrix(versions):
    """Format versions as comma-separated string for use in matrix."""
    return ",".join(versions)


def main():
    file_path = Path(PYPROJECT_FILE)

    if not file_path.exists():
        print(f"versions-matrix=")
        print(f"versions-json=[]")
        print(f"min-version=")
        print(f"max-version=")
        print(f"Error: {PYPROJECT_FILE} not found", file=sys.stderr)
        sys.exit(1)

    try:
        content = file_path.read_text()
    except Exception as e:
        print(f"versions-matrix=")
        print(f"versions-json=[]")
        print(f"min-version=")
        print(f"max-version=")
        print(f"Error reading {PYPROJECT_FILE}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        versions, min_version, max_version = extract_python_versions(content)
    except Exception as e:
        print(f"versions-matrix=")
        print(f"versions-json=[]")
        print(f"min-version=")
        print(f"max-version=")
        print(f"Error parsing Python versions: {e}", file=sys.stderr)
        sys.exit(1)

    # Output all formats
    print(f"versions-matrix={format_matrix(versions)}")
    print(f"versions-json={json.dumps(versions)}")
    print(f"min-version={min_version if min_version else ''}")
    print(f"max-version={max_version if max_version else ''}")


if __name__ == "__main__":
    main()
