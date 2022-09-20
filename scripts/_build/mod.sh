#!/bin/sh

dir="$(dirname "$(CDPATH="" cd -- "$(dirname -- "$0")" && pwd)")/.."
temp="$(mktemp -d)"

build="$dir/build"
mkdir -p "$build"

name="$(perl -ne 'if (/^.*name="([^"]*)"/) { print $1; exit }' "$dir/mod/header.rpy")"
version="$(perl -ne 'if (/^.*version="([^"]*)"/) { print $1; exit }' "$dir/mod/header.rpy")"
package="$(echo "$name" | tr "[:upper:]" "[:lower:]" | tr "[:blank:]" "-")"

mkdir -p "$temp/game/Submods/$name"
mkdir "$temp/game/Submods/$name/config"
cp -r "$dir/mod"/* "$temp/game/Submods/$name"
cp -r "$dir/lib" "$temp/game/Submods/$name"
rm "$temp/game/Submods/$name/lib/README.txt"

(cd "$temp" || exit 1; find game | zip -9@q "$build/$package-$version.zip" && rm -rf "$temp")