# header.rpy contains MAS submod header as well as Submod Updater header.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod

init -990 python in mas_submod_utils:
    Submod(
        author="Friends of Monika",
        name="Discord Presence Submod",
        description="Show everyone who's the person you're spending your time with~",
        version="0.1.0",
        settings_pane="fom_presence_settings_pane",
        version_updates={
            "friends_of_monika_discord_presence_submod_v0_0_1": "friends_of_monika_discord_presence_submod_v0_0_2"
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