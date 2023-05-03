# This Ren'Py script exists to provide upcoming event key IDs, prompts and day
# countdowns as custom variables usable in condition expressions and
# interpolations.
#
# Author: Herman S. <dreamscache.d@gmail.com>
# Since: 0.0.1
#
# Variables:
#   NOTE: the following variables have suffixes (see XXX bit, e.g. eve_days_24h).
#   Suffixes: 24h, 3d, 1w, 1m, 1y (24 hours, 3 days, 1 week, 1 month, 1 year)
#
#   eve_days_XXX - days until next calendar event within specified range
#     or None if there aren't any.
#   eve_prompt_XXX - prompt (with variables interpolated.) of next calendar
#     event within specified range or None if there aren't any.
#   eve_key_XXX - key ID of next calendar event within specified range or None
#     if there aren't any.
#   eve_unit_days_XXX - word "day" or "days" depending on days remaining
#     until the event in the specified range or None if there aren't any.

init 200 python in fom_presence_extensions:

    import store
    from store import _fom_presence_util as util


    events_ignore("milestone_personal_best")


    def _fom_update_eve_vars(n_days, suffix):
        _vars = dict()

        next_eve = _fom_get_next_event(n_days)
        if next_eve is None:
            _vars["eve_days_{0}".format(suffix)] = None
            _vars["eve_prompt_{0}".format(suffix)] = None
            _vars["eve_key_{0}".format(suffix)] = None
            _vars["eve_unit_days_{0}".format(suffix)] = None

        else:
            _vars["eve_days_{0}".format(suffix)] = next_eve[0].days
            _vars["eve_prompt_{0}".format(suffix)] = next_eve[1]
            _vars["eve_key_{0}".format(suffix)] = next_eve[2]
            _vars["eve_unit_days_{0}".format(suffix)] = (
                _fom_get_eve_unit_days(next_eve[0].days))

        return _vars

    def _fom_get_eve_unit_days(n_days):
        if n_days != 1:
            return "days"
        else:
            return "day"

    def _fom_update_eve_vars_all():
        _vars = dict()
        _vars.update(_fom_update_eve_vars(1, "24h"))
        _vars.update(_fom_update_eve_vars(3, "3d"))
        _vars.update(_fom_update_eve_vars(7, "1w"))
        _vars.update(_fom_update_eve_vars(31, "1m"))
        _vars.update(_fom_update_eve_vars(365, "1y"))
        return _vars

    cvars_add_var_set(_fom_update_eve_vars_all)