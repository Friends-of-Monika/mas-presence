#!/bin/sh

dir="$(dirname "$(CDPATH="" cd -- "$(dirname -- "$0")" && pwd)")"
temp="$(mktemp -d)"

build="$dir/build"
mkdir -p "$build"

name="$(perl -ne 'if (/^.*name="([^"]*)"/) { print $1; exit }' "$dir/mod/header.rpy")"
version="$(perl -ne 'if (/^.*version="([^"]*)"/) { print $1; exit }' "$dir/mod/header.rpy")"
package="$(echo "$name" | tr "[:upper:]" "[:lower:]" | tr "[:blank:]" "-")"

mod="$temp/game/Submods/$name"
mkdir -p "$mod"

cp -r "$dir/mod"/* "$mod/$name"
cp -r "$dir/config" "$mod/config"
cp -r "$dir/lib" "$mod/$name"
rm "$mod/lib/README.txt"

(cd "$temp" || exit 1; find game | zip -9@q "$build/$package-$version.zip" && rm -rf "$temp")