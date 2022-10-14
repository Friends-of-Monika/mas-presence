label friends_of_monika_discord_presence_submod_v0_0_1(version="v0_0_1"):
    return

label friends_of_monika_discord_presence_submod_v0_0_2(version="v0_0_2"):
    python:
        def _migrate_friends_of_monika_discord_presence_submod_v0_0_2():
            import os

            def _get_conf_dir():
                if hasattr(store, "fom_presence"):
                    # Pre-refactor version, so adapt.
                    get_script_file = store.fom_presence._get_script_file
                else:
                    # Post-refactor versions use different naming.
                    get_script_file = store._fom_presence_util.get_script_file

                _file = get_script_file(fallback="game/Submods/Discord Presence Submod/updates.rpy")
                return os.path.join("/".join(_file.split("/")[:-1]), "config")

            try:
                # Remove faulty config.
                os.remove(_get_conf_dir() + "/default/configs/events/moni-bday-day copy.conf")
            except:
                pass

        # Run migration function and delete it not to litter the global scope.
        _migrate_friends_of_monika_discord_presence_submod_v0_0_2()
        del _migrate_friends_of_monika_discord_presence_submod_v0_0_2

    return

label friends_of_monika_discord_presence_submod_v0_0_3(version="v0_0_3"):
    return

label friends_of_monika_discord_presence_submod_v0_0_4(version="v0_0_4"):
    return

label friends_of_monika_discord_presence_submod_v0_1_2(version="v0_1_2"):
    return

label friends_of_monika_discord_presence_submod_v0_2_0(version="v0_2_0"):
    python:
        def _migrate_friends_of_monika_discord_presence_submod_v0_2_0():
            import os

            def _get_lib_dir():
                if hasattr(store, "fom_presence"):
                    # Pre-refactor version, so adapt.
                    get_script_file = store.fom_presence._get_script_file
                else:
                    # Post-refactor versions use different naming.
                    get_script_file = store._fom_presence_util.get_script_file

                _file = get_script_file(fallback="game/Submods/Discord Presence Submod/updates.rpy")
                return os.path.join("/".join(_file.split("/")[:-1]), "lib")

            lib_dir = _get_lib_dir()
            for _file in os.listdir(lib_dir):
                if _file == "py2":
                    continue
                os.rename(os.path.join(lib_dir, _file), os.path.join(lib_dir, "py2", _file))

        # Run migration function and delete it not to litter the global scope.
        _migrate_friends_of_monika_discord_presence_submod_v0_2_0()
        del _migrate_friends_of_monika_discord_presence_submod_v0_2_0

    return