# This Ren'Py script exists to provide current location prompt as a custom
# variable usable in condition expressions and interpolations.
#
# Author: Herman S. <dreamscache.d@gmail.com>
# Since: 0.0.1
#
# Variables:
#   loc_prompt - current location prompt (with variables interpolated.)

init 200 python in fom_presence_extensions:

    import store


    def _fom_loc_prompt():
        # Current background is None until MAS sets it on startup.
        bg = store.mas_current_background
        if bg is None:
            return None
        return renpy.substitute(bg.prompt)

    cvars_add_var("loc_prompt", _fom_loc_prompt)