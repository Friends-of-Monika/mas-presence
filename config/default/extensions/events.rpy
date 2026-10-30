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


    def _fom_update_eve_vars(events, n_days, suffix):
        _vars = dict()

        # Events are sorted by days until event, so first one in range is the
        # closest one.
        next_eve = None
        if len(events) > 0 and events[0][0].days < n_days:
            next_eve = events[0]

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
        # Calendar is scanned once for the longest range, shorter ranges
        # just take the closest event if it falls within them.
        events = _fom_get_upcoming_events(365)

        _vars = dict()
        _vars.update(_fom_update_eve_vars(events, 1, "24h"))
        _vars.update(_fom_update_eve_vars(events, 3, "3d"))
        _vars.update(_fom_update_eve_vars(events, 7, "1w"))
        _vars.update(_fom_update_eve_vars(events, 31, "1m"))
        _vars.update(_fom_update_eve_vars(events, 365, "1y"))
        return _vars

    cvars_add_var_set(_fom_update_eve_vars_all)