# logging.rpy contains constants and functions for prefixed logging of
# Discord Presence Submod messages in submod log.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod


init -100 python in fom_presence_logging:

    import store
    from store.mas_submod_utils import submod_log


    class Logger(object):
        def __init__(self, prefix, upstream):
            self._prefix = prefix
            self._upstream = logger

        def debug(self, message):
            self._upstream.debug(self._prefix + message)

        def info(self, message):
            self._upstream.info(self._prefix + message)

        def warning(self, message):
            self._upstream.warn(self._prefix + message)

        def error(self, message):
            self._upstream.error(self._prefix + message)


    LOGGER = Logger(prefix="[Discord Presence Submod] ", upstream=submod_log)