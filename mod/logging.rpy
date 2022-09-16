init -100 python in fom_presence:

    import store
    from store.mas_submod_utils import submod_log


    _LOG_PREFIX = "[Discord Presence Submod] "


    def _debug(msg):
        submod_log.debug(_LOG_PREFIX + msg)

    def _info(msg):
        submod_log.info(_LOG_PREFIX + msg)

    def _warn(msg):
        submod_log.warn(_LOG_PREFIX + msg)

    def _error(msg):
        submod_log.error(_LOG_PREFIX + msg)