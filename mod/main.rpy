# main.rpy is the entrypoint into Discord Presence Submod, containing label
# plugins (hooks) and presence controller, main logic governoring the Rich
# Presence displayed on user's profile.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod


init 100 python in _fom_presence:

    import store

    from store import persistent

    from store import _fom_presence_config as config
    from store import _fom_presence_error as error
    from store import _fom_presence_discord as discord
    from store import _fom_presence_logging as logging

    import socket
    import datetime


    _TIMEOUT_LOCK_DURATION = datetime.timedelta(seconds=45)


    _ERROR_SOCKET_NOT_FOUND = error.Error(
        log_message_report="Could not connect to Discord Rich Presence. Is Discord running locally (not in browser?)",
        log_message_resolve="Established connection with Discord Rich Presence."
    )

    _ERROR_CLIENT_CONNECTION = error.Error(
        log_message_report="Could not connect to Discord RPC: {0}.",
        log_message_resolve="Connection with Discord established.",
        ui_message_report="Could not establish connection with Discord.",
        ui_message_resolve="Connection with Discord established."
    )

    _ERROR_CLIENT_TIMEOUT = error.Error(
        log_message_report="Timed out while connecting to Discord RPC.",
        log_message_resolve="Connection with Discord established.",
        ui_message_report="Discord connection timed out, further attempts will be possible in {0} seconds.".format(int(_TIMEOUT_LOCK_DURATION.total_seconds())),
        ui_message_resolve="Connection with Discord established."
    )

    _ERROR_CLIENT_PINGING = error.Error(
        log_message_report="Connection with Discord lost: {0}.",
        log_message_resolve="Re-established connection with Discord.",
        ui_message_report="Connection with Discord lost. Trying to re-establish it...",
        ui_message_resolve="Connection with Discord re-established."
    )

    _ERROR_CLIENT_ACTIVITY = error.Error(
        log_message_report="Could not set activity: {0}",
        ui_message_report="Could not set Rich Presence activity."
    )


    class _PresenceController(object):

        def __init__(self, logger):
            self._logger = logger
            self._connected = False
            self._config = None
            self._clients = dict()
            self._lock_conn_until = None
            self._last_mean_update = None

        @property
        def connected(self):
            return self._connected

        @property
        def timeout_locked(self):
            return self._lock_conn_until is not None and self._lock_conn_until > datetime.datetime.now()

        @property
        def last_meaningful_update(self):
            return self._last_mean_update

        def connect(self):
            if self._config is None:
                self._config = config.get_active_config()
                if self._config is None:
                    return

            client_with_socket = self._get_or_connect_client(self._config)
            if client_with_socket is None:
                return

            client, _ = client_with_socket
            client.set_activity(self._config.to_activity())
            self._connected = True

        def disconnect(self):
            for app_id in list(self._clients.keys()):
                client, _ = self._clients.pop(app_id)
                client.disconnect()
            self._connected = False

        def update(self):
            if not self._check_all_connections():
                self.disconnect()
                return

            prev_config, self._config = self._config, config.get_active_config()
            if self._config is None:
                client.clear_activity()
                return

            if prev_config.app_id != self._config.app_id:
                prev_client, _ = self._get_or_connect_client(prev_config)
                prev_client.clear_activity()
                return

            if prev_config != self._config:
                self._last_mean_update = datetime.datetime.now()

            client_with_socket = self._get_or_connect_client(self._config)
            if client_with_socket is None:
                return

            try:
                client, _ = client_with_socket
                client.set_activity(self._config.to_activity())
                _ERROR_CLIENT_ACTIVITY.resolve()
            except (discord.ProtocolError, discord.CallError) as e:
                _ERROR_CLIENT_ACTIVITY.report(e)

        def _get_or_connect_client(self, config):
            rpc_socket = self._connect_socket()
            if rpc_socket is None:
                return

            client_with_socket = self._clients.get(config.app_id)
            if client_with_socket is None:
                try:
                    client = discord.Client(rpc_socket)
                    client.handshake(config.app_id)
                    _ERROR_CLIENT_TIMEOUT.resolve()
                    _ERROR_CLIENT_CONNECTION.resolve()
                    self._set_timeout_lock(False)
                except (discord.ProtocolError, discord.CallError) as e:
                    if isinstance(e, discord.ProtocolError) and isinstance(e.args[0], socket.timeout):
                        _ERROR_CLIENT_TIMEOUT.report()
                        self._set_timeout_lock(True)
                    else:
                        _ERROR_CLIENT_CONNECTION.report(e)
                    return None

                self._clients[config.app_id] = (client, rpc_socket)
                return client, rpc_socket

            return client_with_socket

        def _connect_socket(self):
            if self.timeout_locked:
                return None

            try:
                rpc_socket = discord.get_rpc_socket()
                if socket is None:
                    _ERROR_SOCKET_NOT_FOUND.report()
                    return None

                _ERROR_SOCKET_NOT_FOUND.resolve()
                _ERROR_CLIENT_TIMEOUT.resolve()
                self._set_timeout_lock(False)
                return rpc_socket

            except socket.timeout as e:
                self._set_timeout_lock(True)
                _ERROR_CLIENT_TIMEOUT.report()
                return None

        def _set_timeout_lock(self, lock):
            if lock:
                self._lock_conn_until = datetime.datetime.now() + _TIMEOUT_LOCK_DURATION
            else:
                self._lock_conn_until = None

        def _check_all_connections(self):
            for client, _ in self._clients.values():
                try:
                    client.ping()
                except discord.ProtocolError as e:
                    _ERROR_CLIENT_PINGING.report(e)
                    return False

            _ERROR_CLIENT_PINGING.resolve()
            return True


    presence = _PresenceController(logging.DEFAULT)


    # Runs once on startup, but post-init.
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=100)
    def on_preloop():
        if persistent._fom_presence_enabled:
            config.reload_configs()
        if not presence.timeout_locked:
            presence.connect()


    # Runs approximately once per 5 seconds while not in dialogue.
    @store.mas_submod_utils.functionplugin("ch30_loop", priority=100)
    def on_loop():
        if persistent._fom_presence_enabled:
            if presence.connected:
                presence.update()
            elif not presence.timeout_locked:
                presence.connect()


    # Runs on exit.
    @store.mas_submod_utils.functionplugin("exit", priority=100)
    def on_exit():
        if presence.connected:
            presence.disconnect()