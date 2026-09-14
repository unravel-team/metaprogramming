#!/usr/bin/env bash
set -Eeuo pipefail

version_file="VERSION"

read_version() {
  local version
  version="$(tr -d '[:space:]' < "$version_file")"
  if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "VERSION must contain plain semantic version." >&2
    exit 2
  fi
  printf '%s\n' "$version"
}

bump() {
  local kind="$1" major minor patch
  IFS=. read -r major minor patch < <(read_version)
  case "$kind" in
    major) major=$((major + 1)); minor=0; patch=0 ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    patch) patch=$((patch + 1)) ;;
    *) echo "Expected major, minor, or patch." >&2; exit 2 ;;
  esac
  printf '%s.%s.%s\n' "$major" "$minor" "$patch" > "$version_file"
  cat "$version_file"
}

case "${1:-}" in
  version) read_version ;;
  major|minor|patch) bump "$1" ;;
  *) echo "Usage: $0 {version|major|minor|patch}" >&2; exit 2 ;;
esac
