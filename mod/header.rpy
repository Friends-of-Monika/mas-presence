# header.rpy contains MAS submod header as well as Submod Updater header.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod

init -990 python in mas_submod_utils:

    Submod(
        author="Friends of Monika",
        name="Discord Presence Submod",
        description="Show everyone who's the person you're spending your time with~",
        version="0.4.0",
        settings_pane="fom_presence_settings_pane",
        version_updates={
            "friends_of_monika_discord_presence_submod_v0_0_1": "friends_of_monika_discord_presence_submod_v0_0_2",
            "friends_of_monika_discord_presence_submod_v0_0_2": "friends_of_monika_discord_presence_submod_v0_0_3",
            "friends_of_monika_discord_presence_submod_v0_0_3": "friends_of_monika_discord_presence_submod_v0_0_4",
            "friends_of_monika_discord_presence_submod_v0_0_4": "friends_of_monika_discord_presence_submod_v0_1_2",
            "friends_of_monika_discord_presence_submod_v0_1_2": "friends_of_monika_discord_presence_submod_v0_2_0",
            "friends_of_monika_discord_presence_submod_v0_2_0": "friends_of_monika_discord_presence_submod_v0_2_1",
            "friends_of_monika_discord_presence_submod_v0_2_1": "friends_of_monika_discord_presence_submod_v0_3_0",
            "friends_of_monika_discord_presence_submod_v0_3_0": "friends_of_monika_discord_presence_submod_v0_3_1",
            "friends_of_monika_discord_presence_submod_v0_3_1": "friends_of_monika_discord_presence_submod_v0_3_2"
        }
    )


init -989 python:

    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Discord Presence Submod",
            user_name="friends-of-monika",
            repository_name="mas-presence",
            extraction_depth=3
        )


init -100 python in _fom_presence:

    import store

    from store import _fom_presence_util as util

    import os


    basedir = os.path.join(renpy.config.basedir, *util.get_script_file(
        fallback="game/Submods/Discord Presence Submod/config.rpy"
    ).split("/")[:-1])