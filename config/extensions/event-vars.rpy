init 100 python fom_presence_extensions:

    import store
    from store import persistent, mas_background, fom_presence

    def _export(name, value):
        setattr(store, name, value)

    def _update_loc_prompt():
        bg = mas_background.BACKGROUND_MAP[persistent._mas_current_background]
        _export("loc_prompt", renpy.substitute(bg.prompt))


    def _update_eve_vars(n_days, suffix):
        next_eve = fom_presence._get_next_event(n_days)
        if next_eve is None:
            _export("eve_days_{0}".format(suffix), None)
            _export("eve_prompt_{0}".format(suffix), None)
            _export("eve_key_{0}".format(suffix), None)
        else:
            _export("eve_days_{0}".format(suffix), next_eve[0].days)
            _export("eve_prompt_{0}".format(suffix), next_eve[1])
            _export("eve_key_{0}".format(suffix), next_eve[2])


    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-10)
    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-10)
    def update_user_vars():
        # Update loc_prompt variable
        _update_loc_prompt()

        # Update eveXX-variables
        _update_eve_vars(1, "24h")
        _update_eve_vars(3, "3d")
        _update_eve_vars(7, "1w")
        _update_eve_vars(31, "1m")
        _update_eve_vars(365, "1y")