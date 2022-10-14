#!/bin/sh

dir="$(dirname "$(CDPATH="" cd -- "$(dirname -- "$0")" && pwd)")"
find "$dir/config/default/configs" -type f -iname "*.conf" -exec python3 -c '\
import configparser, sys; \
p = configparser.ConfigParser(); \
p.read(sys.argv[1]);
print(sys.argv[1][len(sys.argv[2]) + len("/config/default/configs") + 1:], p.get("Presence", "Priority"))
' \{\} "$dir" \; | sort -n -t" " -k 2 -r