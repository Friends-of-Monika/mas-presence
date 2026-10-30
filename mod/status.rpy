# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/mas-presence

init -90 python in _fom_presence_status:
    from store import _fom_presence_logging as logging

    WARNING = "warning"
    ERROR = "error"

    # Currently active problems, maps key to (level, UI message) tuple.
    _active = dict()

    def set(key, ui_message, log_message=None, level=ERROR):
        """
        Sets an active problem under the provided key, replacing the previous
        one with the same key. The problem is logged only if it is new or its
        UI message or level have changed, so repeated reports are not logged.
        Must be called from the main thread.

        IN:
            key -> str:
                Key of the problem, e.g. "connection" or "config:<file>".

            ui_message -> str:
                Message to display in submod settings pane.

            log_message -> str or None, default None:
                Message to write to log; if None, ui_message is logged.

            level -> str, default ERROR:
                Problem level, either WARNING or ERROR.
        """

        entry = (level, ui_message)
        if _active.get(key) == entry:
            return

        getattr(logging.DEFAULT, level)(log_message if log_message is not None else ui_message)
        _active[key] = entry
        renpy.restart_interaction()

    def clear(key, log_message=None):
        """
        Clears the active problem with the provided key, if any. Must be called
        from the main thread.

        IN:
            key -> str:
                Key of the problem to clear.

            log_message -> str or None, default None:
                Message to write to log if a problem was actually cleared.
        """

        if _active.pop(key, None) is None:
            return

        if log_message is not None:
            logging.DEFAULT.info(log_message)
        renpy.restart_interaction()

    def clear_prefix(prefix):
        """
        Clears all active problems which keys start with the provided prefix.
        Must be called from the main thread.

        IN:
            prefix -> str:
                Key prefix, e.g. "config:".
        """

        keys = [key for key in _active if key.startswith(prefix)]
        for key in keys:
            del _active[key]

        if keys:
            renpy.restart_interaction()

    def entries():
        """
        Returns currently active problems sorted by key.

        OUT:
            list of (key, level, ui_message) tuples.
        """

        return [(key, level, message) for key, (level, message) in sorted(_active.items())]
