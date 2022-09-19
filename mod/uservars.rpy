# uservars.rpy contains user variables dictionary and functions for scheduled
# variables updating that occurs on each presence update loop.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod

init 80 python in fom_presence:

    import store
    from store import persistent, mas_background

    import datetime

    _uservars = dict()
    _uservars_temp = dict()

    def _expose_uservars():
        for key, value in _uservars.items():
            exists = hasattr(store, key)
            if exists:
                _uservars_temp[key] = (getattr(store, key), exists)
            else:
                _uservars_temp[key] = (None, exists)
            setattr(store, key, value)

    def _unexpose_uservars():
        for key, exists in list(_uservars_temp.keys()):
            if exists:
                setattr(store, key, _uservars_temp.pop(key))
            else:
                _uservars_temp.pop(key)
                delattr(store, key)

    def _uservars_eval(s):
        return eval(s, _uservars, store.__dict__)

    def _uservars_subst(s):
        try:
            _expose_uservars()
            return renpy.substitute(s, _uservars)
        finally:
            _unexpose_uservars()


    def _update_funcs():
        _uservars.update(dict(
            lower=lambda s: s.lower(),
            upper=lambda s: s.upper(),
            decap=lambda s: _str_detitle(s)
        ))
        _uservars.update(_uservars)


    def _update_loc_prompt():
        bg = mas_background.BACKGROUND_MAP[persistent._mas_current_background]
        _uservars["loc_prompt"] = renpy.substitute(bg.prompt)

    def _update_eve_remaining(n_days, suffix):
        next_eve = _get_next_event(n_days)
        if next_eve is None:
            _uservars["eve_days_{0}".format(suffix)] = None
            _uservars["eve_prompt_{0}".format(suffix)] = None
            _uservars["eve_key_{0}".format(suffix)] = None
        else:
            _uservars["eve_days_{0}".format(suffix)] = next_eve[0].days
            _uservars["eve_prompt_{0}".format(suffix)] = next_eve[1]
            _uservars["eve_key_{0}".format(suffix)] = next_eve[2]

    def _update_uservars():
        _update_funcs()
        _update_loc_prompt()
        _update_eve_remaining(1, "24h")
        _update_eve_remaining(3, "3d")
        _update_eve_remaining(7, "1w")
        _update_eve_remaining(31, "1m")
        _update_eve_remaining(365, "1y")