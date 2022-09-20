#!/bin/sh

dir="$(dirname "$(CDPATH="" cd -- "$(dirname -- "$0")" && pwd)")/scripts"
"$dir/_build/mod.sh"
"$dir/_build/ext.sh"