# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/mas-presence

init -99 python in _fom_presence_lib:
    import store
    from store import _fom_presence as mod

    import os
    import sys

    if sys.version_info.major == 2:
        sys.path.append(os.path.join(mod.basedir, "lib", "py2"))
