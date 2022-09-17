# settings.rpy contains settings panel rendered in submods menu under
# Discord Presence Submod entry as well as functions invoked on button presses.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod

init 100:

    screen fom_presence_settings_pane:
        $ scr_tooltip = renpy.get_screen("submods", "screens").scope["tooltip"]

        vbox:
            box_wrap False
            xfill True
            xmaximum 800

            hbox:
                style_prefix "check"
                box_wrap False

                textbutton "Enabled":
                    selected persistent._fom_presence_enabled
                    action Function(fom_presence._sscr_toggle)
                    hovered SetField(scr_tooltip, "value", "Enable Discord Rich Presence.")
                    unhovered SetField(scr_tooltip, "value", scr_tooltip.default)

                textbutton "Reconnect":
                    selected False
                    sensitive fom_presence._presence.connected
                    action Function(fom_presence._sscr_reconnect)
                    hovered SetField(scr_tooltip, "value", "Forcibly reconnect to Discord Rich Presence.")
                    unhovered SetField(scr_tooltip, "value", scr_tooltip.default)

                textbutton "Reload":
                    selected False
                    sensitive fom_presence._presence.connected
                    action Function(fom_presence._sscr_reload)
                    hovered SetField(scr_tooltip, "value", "Forcibly reload presence activity.")
                    unhovered SetField(scr_tooltip, "value", scr_tooltip.default)


init 100 python in fom_presence:

    import store
    from store import persistent, fom_presence

    def _sscr_toggle():
        try:
            fom_presence._presence.ectx = _ectx_opts

            persistent._fom_presence_enabled = not persistent._fom_presence_enabled
            if not persistent._fom_presence_enabled and fom_presence._presence.connected:
                fom_presence._presence.disconnect()

            elif persistent._fom_presence_enabled and not fom_presence._presence.connected:
                fom_presence._presence._reconnect()

        finally:
            fom_presence._presence.ectx = _ectx_main

    def _sscr_reconnect():
        try:
            fom_presence._presence.ectx = _ectx_opts
            _presence._reconnect()
        finally:
            fom_presence._presence.ectx = _ectx_main

    def _sscr_reload():
        try:
            fom_presence._presence.ectx = _ectx_opts
            _presence._reload()
        finally:
            fom_presence._presence.ectx = _ectx_main
