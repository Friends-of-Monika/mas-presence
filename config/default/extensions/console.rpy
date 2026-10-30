# This Ren'Py script exists to trigger presence update when player opens
# console.
#
# Author: Herman S. <dreamscache.d@gmail.com>
# Since: 0.4.0

init 300 python in fom_presence_extensions:

    import store

    from store import persistent
    from store import _fom_presence as mod
    from store import _fom_presence_config as config

    @store.mas_submod_utils.functionplugin("_console", priority=100)
    def _fom_console_label_callback():
        # Do not connect if presence is disabled or not connected yet, and do
        # not clear activity if console config is missing (or not loaded yet.)
        if not persistent._fom_presence_enabled or not mod.presence.connected:
            return

        console_config = config.get_config("Console")
        if console_config is not None:
            mod.presence.update(with_config=console_config)