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