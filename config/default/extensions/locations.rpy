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
    from store import persistent, mas_background


    def _fom_loc_prompt():
        bg = mas_background.BACKGROUND_MAP[persistent._mas_current_background]
        return renpy.substitute(bg.prompt)

    cvars_add_var("loc_prompt", _fom_loc_prompt)