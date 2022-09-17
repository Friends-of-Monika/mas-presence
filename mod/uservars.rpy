# uservars.rpy contains user variables dictionary and functions for scheduled
# variables updating that occurs on each presence update loop.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod

init 100 python in fom_presence:

    import store
    from store import persistent, mas_background

    _uservars = dict()

    def _update_loc_prompt():
        bg = mas_background.BACKGROUND_MAP[persistent._mas_current_background]
        prompt = renpy.substitute(bg.prompt)

        if len(prompt) > 0 and prompt[0].isupper():
            # If prompt is Title-cased, decapitalize it.
            prompt = prompt[0].lower() + prompt[1:]

        _uservars["loc_prompt"] = prompt


    def _update_uservars():
        _update_loc_prompt()