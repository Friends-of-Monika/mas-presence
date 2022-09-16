init 100 python in fom_presence:

    import store
    from store import persistent, mas_background

    _ext_vars = dict()

    def _update_loc_prompt():
        bg = mas_background.BACKGROUND_MAP[persistent._mas_current_background]
        prompt = renpy.substitute(bg.prompt)

        if len(prompt) > 0 and prompt[0].isupper():
            # If prompt is Title-cased, decapitalize it.
            prompt = prompt[0].lower() + prompt[1:]

        _ext_vars["loc_prompt"] = prompt


    def _update_uservars():
        _update_loc_prompt()