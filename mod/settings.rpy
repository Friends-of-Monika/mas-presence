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
                action Function(fom_presence._sscr_reconnect)
                hovered SetField(scr_tooltip, "value", "Forcibly reconnect to Discord Rich Presence.")
                unhovered SetField(scr_tooltip, "value", scr_tooltip.default)

            textbutton "Reload":
                selected False
                action Function(fom_presence._sscr_reload)
                hovered SetField(scr_tooltip, "value", "Forcibly reload current activity.")
                unhovered SetField(scr_tooltip, "value", scr_tooltip.default)