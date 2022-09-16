init -990 python in mas_submod_utils:
    Submod(
        author="Friends of Monika",
        name="Discord Presence Submod",
        description="Show everyone who's the person you're spending your time with~",
        version="1.0.0",
        settings_pane="fom_presence_settings_pane"
    )

init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Discord Presence Submod",
            user_name="friends-of-monika",
            repository_name="presence-submod",
            extraction_depth=3
        )