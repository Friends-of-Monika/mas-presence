# This Ren'Py script exists to provide additional functionality such as current
# location prompt, upcoming event key IDs, prompts and day countdowns as well
# as some utility functions that will also be exposed to global scope.
#
# Author: Herman S. <dreamscache.d@gmail.com>
#
# Full list of variables and functions follows:
# Variables:
#   loc_prompt - current location prompt (with variables interpolated.)
#
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
#
# Functions:
#
#  upper(s) - transform a string into uppercase.
#  lower(s) - transform a string into lowercase.
#
#  title(s) - transform a string into titlecase, make first character uppercase
#    and leave all the other characters lowercase.
#  decapitalize(s) - transform only the first character of a string to
#   lowercase.

init 200 python in fom_presence_extensions:

    import store
    from store import mas_background


    # LOCATION PROMPT VARIABLE

    def _fom_loc_prompt():
        bg = mas_background.BACKGROUND_MAP[persistent._mas_current_background]
        return renpy.substitute(bg.prompt)
    cvars_add_var("loc_prompt", _fom_loc_prompt)


    # UPCOMING CALENDAR EVENT VARIABLES

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


    # STRING FUNCTIONS

    def _update_str_funcs():
        _vars = dict()

        def upper(s):
            return s.upper()
        _vars["upper"] = upper

        def lower(s):
            return s.lower()
        _vars["lower"] = lower

        def title(s):
            return s.title()
        _vars["title"] = title

        def decapitalize(s):
            if len(s) == 0:
                return s
            return s[0].lower() + s[1:]
        _vars["decapitalize"] = decapitalize

        return _vars
    cvars_add_var_set(_update_str_funcs, loop=False)