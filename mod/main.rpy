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


    _ERROR_SOCKET_UNAVAILABLE = error.Error(
        log_message_report="Could not establish connection with Discord RPC socket.",
        log_message_resolve="Established connection with Discord RPC socket."
    )

    _ERROR_CLIENT_CONNECTION = error.Error(
        log_message_report="Could not connect to Discord RPC with application ID {0}: {1}",
        log_message_resolve="Connection with Discord established.",
        ui_message_report="Could not establish connection with Discord. It is most likely rate limited,\n"
                          "for more details see log/submod_log.log.",
        ui_message_resolve="Connection with Discord established."
    )

    _ERROR_CLIENT_PINGING = error.Error(
        log_message_report="Connection with Discord lost: could not ping client {0}: {1}",
        log_message_resolve="Re-established connection with Discord.",
        ui_message_report="Connection with Discord lost. Trying to re-establish it...",
        ui_message_resolve="Connection with Discord re-established."
    )

    _ERROR_CLIENT_ACTIVITY = error.Error(
        log_message_report="Could not set activity: {0}",
        ui_message_report="Could not set Rich Presence activity.\n"
                          "For more details see log/submod_log.log"
    )


    class _PresenceController(object):

        def __init__(self, logger):
            self._logger = logger

            self._connected = False
            self._config = None

            self._socket = None
            self._clients = dict()

        @property
        def connected(self):
            return self._connected

        def connect(self):
            if self._config is None:
                self._config = config.get_active_config()
                if self._config is None:
                    return

            client_with_data = self._get_or_connect_client(self._config)
            if client_with_data is None:
                return

            client, _ = client_with_data
            client.set_activity(self._config.to_activity())
            self._connected = True

        def disconnect(self):
            for app_id in list(self._clients.keys()):
                client, _ = self._clients.pop(app_id)
                client.disconnect()
            self._socket = None
            self._connected = False

        def update(self):
            if not self._check_all_connections():
                self.disconnect()
                return

            prev_config, self._config = self._config, config.get_active_config()
            if not self._config:
                prev_client.clear_activity()
                return

            if prev_config.app_id != self._config.app_id:
                prev_client = self._get_or_connect_client(prev_config)
                prev_client.clear_activity()

            client_with_data = self._get_or_connect_client(self._config)
            if client_with_data is None:
                return

            try:
                client, _ = client_with_data
                client.set_activity(self._config.to_activity())
                _ERROR_CLIENT_ACTIVITY.resolve()
            except (discord.ProtocolError, discord.CallError) as e:
                _ERROR_CLIENT_ACTIVITY.report(e)

        def _get_or_connect_client(self, config):
            socket = self._get_or_connect_socket()
            if socket is None:
                return

            client_with_data = self._clients.get(config.app_id)
            if client_with_data is None:
                try:
                    client = discord.Client(socket)
                    data = client.handshake(config.app_id)
                except discord.ProtocolError as e:
                    _ERROR_CLIENT_CONNECTION.report(config.app_id, e)
                    return None

                self._clients[config.app_id] = (client, data)
                return client, data

            _ERROR_CLIENT_CONNECTION.resolve()
            return client_with_data

        def _get_or_connect_socket(self):
            if self._socket is None:
                self._socket = discord.get_rpc_socket()
                if self._socket is None:
                    _ERROR_SOCKET_UNAVAILABLE.report()
                return self._socket

            _ERROR_SOCKET_UNAVAILABLE.resolve()
            return self._socket

        def _check_all_connections(self):
            for client, _ in self._clients.values():
                try:
                    client.ping()
                except discord.ProtocolError as e:
                    _ERROR_CLIENT_PINGING.report(app_id, e)
                    return False

            _ERROR_CLIENT_PINGING.resolve()
            return True


    presence = _PresenceController(logging.DEFAULT)


    # Runs once on startup, but post-init.
    @store.mas_submod_utils.functionplugin("ch30_preloop")
    def on_preloop():
        if persistent._fom_presence_enabled:
            config.reload_configs()
            presence.connect()


    # Runs approximately once per 5 seconds while not in dialogue.
    @store.mas_submod_utils.functionplugin("ch30_loop")
    def on_loop():
        if persistent._fom_presence_enabled:
            if presence.connected:
                presence.update()
            else:
                presence.connect()


    # Runs on exit.
    @store.mas_submod_utils.functionplugin("exit")
    def ons_exit():
        if presence.connected:
            presence.disconnect()