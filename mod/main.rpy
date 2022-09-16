init 100 python in fom_presence:

    class _PresenceController(object):
        def __init__(self):
            self._client = None
            self._connected = False
            self._prev_conf = None

        @property
        def connected(self):
            return self._connected

        def connect(self):
            conf = get_active_config()
            if conf is None:
                return

            try:
                cl = Client(get_rpc_socket())
                cl.handshake(conf.app_id)

            except (CallError, IOError) as e:
                # TODO: Notify user with a toast message
                _error("Could not connect to Discord IPC socket: {0}".format(e))
                return

            try:
                _update_uservars()
                cl.set_activity(conf.activity)

            except (CallError, IOError) as e:
                # TODO: Notify user with a toast message
                _error("Could not set initial activity: {0}".format(e))
                return

            self._client = cl
            self._connected = True
            self._prev_conf = conf

        def disconnect(self):
            self._client.disconnect()
            self._connected = False
            self._prev_conf = None

        def update(self):
            conf = get_active_config()
            if conf is None:
                self.disconnect()
                return

            try:
                self._client.ping()

            except (CallError, IOError) as e:
                # TODO: Notify user with a toast message
                self.disconnect()
                return

            _update_uservars()
            self._client.set_activity(conf.activity)
            self._prev_conf = conf

    _presence = _PresenceController()


    # Runs once on startup, but post-init.
    @store.mas_submod_utils.functionplugin("ch30_preloop")
    def _preloop():
        _load_configs()
        _presence.connect()


    # Runs approximately once per 5 seconds while not in dialogue.
    @store.mas_submod_utils.functionplugin("ch30_loop")
    def _loop():
        _update_uservars()
        _presence.update()


    # Runs on exit.
    @store.mas_submod_utils.functionplugin("exit")
    def _exit():
        _presence.disconnect()
