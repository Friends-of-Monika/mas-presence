# lib.rpy performs Python module lookup path modifications in order to enable
# Python modules from lib/ folder to work with Ren'Py 6 distribution of MAS.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod


init -999 python in _fom_presence_lib:

    import sys


    if sys.version_info.major == 2:
        def _get_lib_dir():
            _file = _get_script_file(fallback="game/Submods/Discord Presence Submod/lib.rpy")
            return os.path.join(renpy.config.basedir, "/".join(_file.split("/")[:-1]), "lib")

        sys.path.append(_get_lib_dir())