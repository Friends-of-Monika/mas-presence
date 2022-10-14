# settings.rpy contains settings panel rendered in submods menu under
# Discord Presence Submod entry as well as functions invoked on button presses.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod

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


init 100 python in _fom_presence_settings:

    import store

    from store import persistent
    from store import _fom_presence as mod
    from store import _fom_presence_config as config
    from store import _fom_presence_error as error


    def toggle():
        with error.temporary_context(error.OPTIONS_CONTEXT):
            persistent._fom_presence_enabled = not persistent._fom_presence_enabled
            if not persistent._fom_presence_enabled and mod.presence.connected:
                mod.presence.disconnect()
            elif persistent._fom_presence_enabled and not mod.presence.connected:
                mod.presence.connect()

    def reconnect():
        with error.temporary_context(error.OPTIONS_CONTEXT):
            if mod.presence.connected:
                mod.presence.disconnect()
            mod.presence.connect()

    def reload_activity():
        with error.temporary_context(error.OPTIONS_CONTEXT):
            mod.presence.update()

    def reload_configs():
        with error.temporary_context(error.OPTIONS_CONTEXT):
            config.reload_configs()
