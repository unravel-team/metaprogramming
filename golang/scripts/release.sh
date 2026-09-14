#!/usr/bin/env bash
# Local semantic-version operations for the copied Go scaffold.
# [tag:go-tag-release] Go module versions publish through annotated VCS tags.
set -Eeu -o pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
version_file="$root/VERSION"
module_file="$root/go.mod"
semver='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'

read_version() {
	local version
	version=$(<"$version_file")
	if [[ ! $version =~ $semver ]]; then
		echo "VERSION must contain a plain semantic version." >&2
		exit 2
	fi
	printf '%s\n' "$version"
}

validate_module() {
	local version=$1
	local major module_path
	IFS=. read -r major _ <<<"$version"
	module_path=$(awk '$1 == "module" { print $2; exit }' "$module_file")
	if [[ -z $module_path ]]; then
		echo "go.mod must declare a module path." >&2
		exit 2
	fi
	if ((major >= 2)) && [[ $module_path != */v"$major" ]]; then
		echo "Go v$major releases require go.mod module path ending in /v$major." >&2
		exit 2
	fi
}

bump() {
	local part=$1
	local current major minor patch next
	current=$(read_version)
	IFS=. read -r major minor patch <<<"$current"
	case $part in
	major)
		((major += 1))
		minor=0
		patch=0
		;;
	minor)
		((minor += 1))
		patch=0
		;;
	patch)
		((patch += 1))
		;;
	esac
	next="$major.$minor.$patch"
	validate_module "$next"
	printf '%s\n' "$next" >"$version_file"
	printf '%s\n' "$next"
}

if (($# == 0)); then
	echo "usage: release.sh {version|major|minor|patch|validate-module} [version]" >&2
	exit 2
fi

case $1 in
version)
	(($# == 1)) || { echo "version takes no arguments." >&2; exit 2; }
	read_version
	;;
major|minor|patch)
	(($# == 1)) || { echo "$1 takes no arguments." >&2; exit 2; }
	bump "$1"
	;;
validate-module)
	(($# == 2)) || { echo "validate-module requires a version." >&2; exit 2; }
	[[ $2 =~ $semver ]] || { echo "Version must be plain semantic version." >&2; exit 2; }
	validate_module "$2"
	;;
*)
	echo "usage: release.sh {version|major|minor|patch|validate-module} [version]" >&2
	exit 2
	;;
esac
