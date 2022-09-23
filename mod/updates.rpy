label friends_of_monika_discord_presence_submod_v0_0_1(version="v0_0_1"):
    return

label friends_of_monika_discord_presence_submod_v0_0_2(version="v0_0_2"):
    python:
        import os

        def _get_conf_dir():
            _file = store.fom_presence._get_script_file(fallback="game/Submods/Discord Presence Submod/updates.rpy")
            return os.path.join("/".join(_file.split("/")[:-1]), "config")

        _conf_dir = _get_conf_dir()
        del _get_conf_dir

        try:
            os.remove(_conf_dir + "/default/configs/events/moni-bday-day copy.conf")

        except:
            pass

        del _conf_dir

    return