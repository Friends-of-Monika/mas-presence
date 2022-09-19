# This Ren'Py script exists to provide upcoming event key IDs, prompts and day
# countdowns as custom variables usable in condition expressions and
# interpolations.
#
# Author: Herman S. <dreamscache.d@gmail.com>
#
# Variables:
#   eve_days_24h - days until next calendar event within 24
#     hours or None if there aren't any.
#   eve_prompt_24h - prompt (with variables interpolated.) of next calendar
#     event within 24 hours or None if there aren't any.
#   eve_key_24h - key ID of next calendar event within 24 hours or None if there
#     aren't any.
#
#   eve_days_3d - days until next calendar event within 3 days or None if there
#     aren't any.
#   eve_prompt_3d - prompt (with variables interpolated.) of next calendar event
#     within 3 days or None if there aren't any.
#   eve_key_3d - key ID of next calendar event within 3 days or None if there
#     aren't any.
#
#   eve_days_1w - days until next calendar event within 1 week or None if there
#     aren't any.
#   eve_prompt_1w - prompt (with variables interpolated.) of next calendar event
#     within 1 week or None if there aren't any.
#   eve_key_1w - key ID of next calendar event within 1 week or None if there
#     aren't any.
#
#   eve_days_1m - days until next calendar event within 1 month or None if there
#     aren't any.
#   eve_prompt_1m - prompt (with variables interpolated.) of next calendar event
#     within 1 month or None if there aren't any.
#   eve_key_1m - key ID of next calendar event within 1 month or None if there
#     aren't any.
#
#   eve_days_1y - days until next calendar event within 1 year or None if there
#     aren't any.
#   eve_prompt_1y - prompt (with variables interpolated.) of next calendar event
#     within 1 year or None if there aren't any.
#   eve_key_1y - key ID of next calendar event within 1 year or None if there
#     aren't any.

init 200 python in fom_presence_extensions:

    import store
    from store import fom_presence


    def _fom_update_eve_vars(n_days, suffix):
        _vars = dict()

        next_eve = fom_presence._get_next_event(n_days)
        if next_eve is None:
            _vars["eve_days_{0}".format(suffix)] = None
            _vars["eve_prompt_{0}".format(suffix)] = None
            _vars["eve_key_{0}".format(suffix)] = None
        else:
            _vars["eve_days_{0}".format(suffix)] = next_eve[0].days
            _vars["eve_prompt_{0}".format(suffix)] = next_eve[1]
            _vars["eve_key_{0}".format(suffix)] = next_eve[2]

        return _vars

    def _fom_update_eve_vars_all():
        _vars = dict()
        _vars.update(_fom_update_eve_vars(1, "24h"))
        _vars.update(_fom_update_eve_vars(3, "3d"))
        _vars.update(_fom_update_eve_vars(7, "1w"))
        _vars.update(_fom_update_eve_vars(31, "1m"))
        _vars.update(_fom_update_eve_vars(365, "1y"))
        return _vars

    cvars_add_var_set(_fom_update_eve_vars_all)