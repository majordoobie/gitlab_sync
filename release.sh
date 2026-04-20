#!/usr/bin/env bash
set -euo pipefail

VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from pyproject.toml"
    exit 1
fi

TAG="v$VERSION"

echo "Creating tag: $TAG"

git tag -a "$TAG" -m "Release $TAG"

echo "Tag $TAG created successfully"
echo "Push to air-gapped network with: git push origin $TAG"
