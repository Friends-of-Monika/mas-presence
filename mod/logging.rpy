# logging.rpy contains constants and functions for prefixed logging of
# Discord Presence Submod messages in submod log.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod


init -100 python in _fom_presence_logging:

    import store

    from store.mas_submod_utils import submod_log


    class Logger(object):
        """
        Logger that wraps Monika After Story logging system and augments it with
        prefix.
        """

        def __init__(self, prefix, upstream):
            """
            Creates a new Logger instance with the provided prefix and upstream
            logger to pass logged messages to.

            IN:
                prefix -> str:
                    Prefix to use for this logger. It will be prepended to all
                    messages as is, no extra whitespace will be added. Users
                    should account for that themselves.

                upstream -> logger:
                    Monika After Story upstream logger to pass messages to.
            """

            self._prefix = prefix
            self._upstream = upstream

        def debug(self, message):
            """
            Log a debug message.

            IN:
                message -> str:
                    Message to log.
            """

            self._upstream.debug(self._prefix + message)

        def info(self, message):
            """
            Log a info message.

            IN:
                message -> str:
                    Message to log.
            """

            self._upstream.info(self._prefix + message)

        def warning(self, message):
            """
            Log a warning message.

            IN:
                message -> str:
                    Message to log.
            """

            self._upstream.warn(self._prefix + message)

        def error(self, message):
            """
            Log a error message.

            IN:
                message -> str:
                    Message to log.
            """

            self._upstream.error(self._prefix + message)


    DEFAULT = Logger(prefix="[Discord Presence Submod] ", upstream=submod_log)