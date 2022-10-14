# This Ren'Py script exists to provide functions as custom functions usable in
# condition expressions and interpolations.
#
# Author: Herman S. <dreamscache.d@gmail.com>
# Since: 0.0.1
#
# Functions:
#  upper(s) - transform a string into uppercase.
#  lower(s) - transform a string into lowercase.
#  title(s) - transform a string into titlecase, make first character uppercase
#    and leave all the other characters lowercase.
#  decap(s) - transform only the first character of a string to
#   lowercase.

init 200 python in fom_presence_extensions:

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

        def decap(s):
            if len(s) == 0:
                return s
            return s[0].lower() + s[1:]
        _vars["decap"] = decap

        return _vars

    cvars_add_var_set(_update_str_funcs, loop=False)