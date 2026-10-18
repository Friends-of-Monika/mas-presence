# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/mas-presence

init 100:

    screen fom_presence_settings_pane:
        $ tooltip = renpy.get_screen("submods", "screens").scope["tooltip"]

        vbox:
            box_wrap False
            xfill True
            xmaximum 800

            hbox:
                style_prefix "check"
                box_wrap False

                vbox:
                    textbutton "Enable":
                        selected persistent._fom_presence_enabled
                        sensitive not (_fom_presence.presence.timeout_locked and not _fom_presence.presence.connected)
                        action Function(_fom_presence_settings.toggle)
                        hovered SetField(tooltip, "value", "Enable Discord Rich Presence.")
                        unhovered SetField(tooltip, "value", tooltip.default)

                    textbutton "Reconnect":
                        selected False
                        sensitive persistent._fom_presence_enabled and not _fom_presence.presence.timeout_locked
                        action Function(_fom_presence_settings.reconnect)
                        hovered SetField(tooltip, "value", "Forcibly reconnect to Discord Rich Presence.")
                        unhovered SetField(tooltip, "value", tooltip.default)

                vbox:
                    textbutton "Reload activity":
                        selected False
                        sensitive _fom_presence.presence.connected
                        action Function(_fom_presence_settings.reload_activity)
                        hovered SetField(tooltip, "value", "Forcibly reload presence activity.")
                        unhovered SetField(tooltip, "value", tooltip.default)

                    textbutton "Reload configs":
                        selected False
                        action Function(_fom_presence_settings.reload_configs)
                        hovered SetField(tooltip, "value", "Reload presence configs.")
                        unhovered SetField(tooltip, "value", tooltip.default)

            null height 10

            text _fom_presence_settings.get_headline():
                style "main_menu_version"
                substitute False

            for _key, _level, _message in _fom_presence_status.entries():
                text _fom_presence_settings.escape_text(_message):
                    style "main_menu_version"
                    color _fom_presence_settings.LEVEL_COLORS[_level]
                    substitute False

        # Keep lock countdown in headline ticking.
        if _fom_presence.presence.timeout_locked:
            timer 1.0 repeat True action Function(renpy.restart_interaction)


init 100 python in _fom_presence_settings:

    import store

    from store import persistent
    from store import _fom_presence as mod
    from store import _fom_presence_config as config
    from store import _fom_presence_status as status


    LEVEL_COLORS = {
        status.WARNING: "#d98c00",
        status.ERROR: "#d63a3a"
    }


    def toggle():
        persistent._fom_presence_enabled = not persistent._fom_presence_enabled
        if not persistent._fom_presence_enabled:
            mod.presence.disconnect()
        elif not mod.presence.connected:
            mod.presence.connect()

    def reconnect():
        if mod.presence.connected:
            mod.presence.disconnect()
        mod.presence.connect()

    def reload_activity():
        mod.presence.update()

    def reload_configs():
        config.reload_configs()

    def get_headline():
        """
        Returns status headline displayed in settings pane.
        """

        if not persistent._fom_presence_enabled:
            return "Status: disabled"
        if mod.presence.connected:
            return "Status: connected"
        if mod.presence.connecting:
            return "Status: connecting..."

        remaining = mod.presence.timeout_lock_remaining
        if remaining is not None:
            return "Status: not connected, retrying in {0} seconds".format(remaining)
        return "Status: not connected"

    def escape_text(message):
        """
        Escapes Ren'Py text tags in message (e.g. from exception messages.)
        """

        return message.replace("{", "{{")
