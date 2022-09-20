# This Ren'Py script exists to integrate this Discord Presence Submod extensions
# pack with Monika After Story submod framework as well as Submod Updater.
#
# Author: Herman S. <dreamscache.d@gmail.com>

init -990 python:
    store.mas_submod_utils.Submod(
        author="Friends of Monika",
        name="Base Extensions for Discord Presence Submod",
        description="This submod provides Custom Variables framework as well "
                    "as string functions, location prompts, event prompts, "
                    "etc.",
        version="1.0.0"
    )

init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Base Extensions for Discord Presence Submod",
            user_name="friends-of-monika",
            repository_name="discord-presence-submod",
            attachment_id=1
        )