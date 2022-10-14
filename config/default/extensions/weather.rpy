# This Ren'Py script exists to provide current weather prompt as a custom
# variable usable in condition expressions and interpolations.
#
# Author: Herman S. <dreamscache.d@gmail.com>
# Since: 0.1.2
#
# Variables:
#   wth_prompt - current weather prompt (with variables interpolated.)

init 200 python in fom_presence_extensions:

    import store


    def _fom_wth_prompt():
        return renpy.substitute(store.mas_current_weather.prompt)

    cvars_add_var("wth_prompt", _fom_wth_prompt)