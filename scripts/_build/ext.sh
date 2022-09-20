#!/bin/sh

dir="$(dirname "$(CDPATH="" cd -- "$(dirname -- "$0")" && pwd)")/.."
temp="$(mktemp -d)"

build="$dir/build"
mkdir -p "$build"

submod_name="$(perl -ne 'if (/^.*name="([^"]*)"/) { print $1; exit }' "$dir/mod/header.rpy")"

find "$dir/config" -mindepth 1 -maxdepth 1 | while read -r ext; do
    name="$(perl -ne 'if (/^.*name="([^"]*)"/) { print $1; exit }' "$ext/header.rpy")"
    version="$(perl -ne 'if (/^.*version="([^"]*)"/) { print $1; exit }' "$ext/header.rpy")"
    package="$(echo "$name" | tr "[:upper:]" "[:lower:]" | tr "[:blank:]" "-")"

    config="$temp/game/Submods/$submod_name/config"
    mkdir -p "$config"

    cp -r "$ext" "$config"
    (cd "$config" || exit 1; find . | zip -9@q "$build/$package-$version.zip" && rm -rf "$temp")
done