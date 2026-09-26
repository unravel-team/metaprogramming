#!/bin/sh
# [tag:go_hegel_engine] Install the locked module's engine at .tools/libhegel; no test-time setup.
set -eu
cd "$(dirname "$0")/.."
platform="$(go env GOOS)-$(go env GOARCH)"
case "$platform" in
    darwin-arm64) extension=dylib ;;
    linux-amd64|linux-arm64) extension=so ;;
    windows-amd64|windows-arm64) extension=dll ;;
    *) echo "Hegel has no bundled native engine for $platform." >&2; exit 2 ;;
esac
module=$(go list -mod=readonly -m -f '{{.Dir}}' hegel.dev/go/hegel)
source="$module/internal/libhegel/libs/libhegel-$platform.$extension"
[ -s "$source" ] || { echo "Hegel native dependency missing; run make init." >&2; exit 2; }
# Protect the local install destination; never follow an existing symlink.
[ ! -L .tools ] && [ ! -L .tools/libhegel ] || {
    echo "Refusing symlink Hegel installation path." >&2; exit 2;
}
mkdir -p .tools
cp "$source" .tools/libhegel
chmod 755 .tools/libhegel
