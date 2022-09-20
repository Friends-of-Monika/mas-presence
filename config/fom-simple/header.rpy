# This Ren'Py script exists to integrate this presence config pack with Monika
# After Story submod framework as well as Submod Updater.
#
# Author: Herman S. <dreamscache.d@gmail.com>

init -990 python:
    store.mas_submod_utils.Submod(
        author="Friends of Monika",
        name="Simple Presence Config for Discord Presence Submod",
        description="This submod provides simple pack of presence configs such "
                    "as day/night specific presence layouts, special events, "
                    "etc.",
        version="1.0.0",
        dependencies={
            "Base Extensions for Discord Presence Submod": (None, None)
        },
    )

init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Simple Presence Config for Discord Presence Submod",
            user_name="friends-of-monika",
            repository_name="discord-presence-submod",
            attachment_id=2
        )