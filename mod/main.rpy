init 100 python in fom_presence:

    class _PresenceController(object):
        def __init__(self):
            self._client = None
            self._connected = False
            self._curr_conf = None

        @property
        def connected(self):
            return self._connected

        def connect(self):
            if self._curr_conf is None:
                # On first loop, this may be None, so we need to pick it.
                self._curr_conf = get_active_config()
                if self._curr_conf is None:
                    # Refuse to connect if there isn't an active config.
                    return

            self._reconnect()

        def _reconnect(self):
            if self._connected:
                self.disconnect()
            self._connect_with_conf(self._curr_conf)

        def _connect_with_conf(self, conf):
            try:
                cl = Client(get_rpc_socket())
                cl.handshake(conf.app_id)

            except (CallError, IOError) as e:
                # TODO: Notify user with a toast message
                _error("Could not connect to Discord RPC: {0}".format(e))
                return

            try:
                _update_uservars()
                cl.set_activity(conf.activity)

            except Exception as e:
                # TODO: Notify user with a toast message
                _error("Could not set initial activity: {0}".format(e))
                return

            self._client = cl
            self._connected = True

        def disconnect(self):
            try:
                # Try disconnecting, we may ignore the errors though.
                self._client.disconnect()

            except IOError as e:
                # TODO: Notify user with a toast message
                _error("Could not safely close Discord RPC: {0}".format(e))

            # We closed the connection from our side anyway, consider it closed.
            self._connected = False

        def update(self):
            self._curr_conf = get_active_config()
            if conf is None:
                # Disconnect if there isn't any active configs anymore.
                self.disconnect()
                return

            self.reload()

        def _reload(self):
            self._update_with_conf(slf, self._curr_conf)

        def _update_with_conf(self, conf):
            try:
                self._client.ping()

            except (CallError, IOError) as e:
                # TODO: Notify user with a toast message
                _error("Discord RPC is not responding: {0}".format(e))
                self.disconnect()
                return

            try:
                _update_uservars()
                self._client.set_activity(conf.activity)

            except Exception as e:
                # TODO: Notify user with a toast message
                _error("Could not set Rich Presence activity: {0}".format(e))


    _presence = _PresenceController()


    # Runs once on startup, but post-init.
    @store.mas_submod_utils.functionplugin("ch30_preloop")
    def _preloop():
        _load_configs()
        _presence.connect()


    # Runs approximately once per 5 seconds while not in dialogue.
    @store.mas_submod_utils.functionplugin("ch30_loop")
    def _loop():
        if _presence.connected:
            _presence.update()
        else:
            _presence.connect()


    # Runs on exit.
    @store.mas_submod_utils.functionplugin("exit")
    def _exit():
        if _presence.connected:
            _presence.disconnect()
