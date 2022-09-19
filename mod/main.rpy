# main.rpy is the entrypoint into Discord Presence Submod, containing label
# plugins (hooks) and presence controller, main logic governoring the Rich
# Presence displayed on user's profile.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod

init 100 python in fom_presence:

    class _PresenceController(object):
        def __init__(self):
            self.ectx = _ectx_main
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

                self.ectx.resolve(_ERR_PIN)
                self.ectx.resolve(
                    _ERR_CON, "Connection with Discord established."
                )

            except (CallError, ProtocolError) as e:
                _error("Could not connect to Discord RPC: {0}".format(e))
                self.ectx.report(
                    _ERR_CON,
                    "Could not connect to Discord. Ensure it is running or\n"
                    "see details in log/submod_log.log"
                )

                return

            try:
                cl.set_activity(conf.activity)

                self.ectx.resolve(
                    _ERR_ACT, "Presence activity updated."
                )

            except Exception as e:
                _error("Could not set initial activity: {0}".format(e))
                self.ectx.report(
                    _ERR_ACT,
                    "Could not update presence activity. Ensure Discord is "
                    "running or\nsee details in log/submod_log.log"
                )

                return

            self._client = cl
            self._connected = True

        def disconnect(self):
            try:
                # Try disconnecting, we may ignore the errors though.
                self._client.disconnect()

            except IOError as e:
                _error("Could not safely close Discord RPC: {0}".format(e))

            # We closed the connection from our side anyway, consider it closed.
            self._connected = False

        def update(self):
            self._curr_conf = get_active_config()
            if self._curr_conf is None:
                # Disconnect if there isn't any active configs anymore.
                self.disconnect()
                return

            self._reload()

        def _reload(self):
            self._update_with_conf(self._curr_conf)

        def _update_with_conf(self, conf):
            try:
                self._client.ping()

                self.ectx.resolve(
                    _ERR_PIN, "Connection with Discord re-established."
                )

            except (CallError, IOError) as e:
                _error("Discord RPC is not responding: {0}".format(e))
                self.ectx.report(
                    _ERR_PIN,
                    "Discord is not responding. Ensure it is running or\n"
                    "see details in log/submod_log.log"
                )

                self.disconnect()
                return

            try:
                self._client.set_activity(conf.activity)

                self.ectx.resolve(
                    _ERR_ACT, "Presence activity updated."
                )

            except Exception as e:
                _error("Could not set Rich Presence activity: {0}".format(e))
                self.ectx.report(
                    _ERR_ACT,
                    "Could not update presence activity. Ensure Discord is "
                    "running or\nsee details in log/submod_log.log"
                )


    _presence = _PresenceController()


    # Runs once on startup, but post-init.
    @store.mas_submod_utils.functionplugin("ch30_preloop")
    def _preloop():
        _load_configs()

        if persistent._fom_presence_enabled:
            _presence.connect()


    # Runs approximately once per 5 seconds while not in dialogue.
    @store.mas_submod_utils.functionplugin("ch30_loop")
    def _loop():
        if persistent._fom_presence_enabled:
            if _presence.connected:
                _presence.update()
            else:
                _presence.connect()


    # Runs on exit.
    @store.mas_submod_utils.functionplugin("exit")
    def _exit():
        if _presence.connected:
            _presence.disconnect()
