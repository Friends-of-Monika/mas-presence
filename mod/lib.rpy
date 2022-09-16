init -999 python in fom_presence:

    import sys


    if sys.version_info.major == 2:
        def _get_lib_dir():
            _file = _get_script_file(fallback="game/Submods/Discord Presence Submod")
            return os.path.join("/".join(_file.split("/")[:-1]), "lib")

        sys.path.append(_get_lib_dir())