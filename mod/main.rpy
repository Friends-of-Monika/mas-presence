init -99 python in fom_presence:

    _client = None
    _prev_conf = None

    def _connect_client(conf):
        global _client
        _client = Client(get_rpc_socket())
        _client.handshake(conf.app_id)

    def _disconnect_client():
        try:
            # Try closing the socket, but disregard any errors.
            _client.close()

        except (IOError, CallError) as e:
            # Discard error that arose during the close.
            pass

        global _client
        _client = None

    def _update_presence():
        # Load .ini files and evaluate their conditions and priorities to
        # determine one that will be chosen for this presence update.
        conf = get_active_config()
        if conf is None:
            # No active configs. Disconnect the client if it is connected.
            if _client is not None:
                _disconnect_client()
            return

        if _client is None:
            # On first loop there just isn't any client.
            _connect_client(conf)

        else:
            # On consecutive loops, we need to ensure socket still replies.

            try:
                # Ensure socket is still responsive.
                _client.ping()

            except (IOError, CallError) as e:
                # If pinging failed, close the connection.
                _disconnect_client()
                return

        if _prev_conf is not None and conf.app_id != _prev_conf.app_id:
            # If application IDs mismatch, we need to reconnect.
            _disconnect_client()
            _connect_client(conf)

        # Set activity from this presence config.
        _client.set_activity(conf.to_activity())

        # Keep a previous config for sake of application ID matching and related
        # checks on future loops.
        global _prev_conf
        _prev_conf = conf


    # Runs once on startup, but post-init.
    @store.mas_submod_utils.functionplugin("ch30_preloop")
    def _preloop():
        _load_configs()
        _update_loc_prompt()
        _update_presence()


    # Runs approximately once per 5 seconds while not in dialogue.
    @store.mas_submod_utils.functionplugin("ch30_loop")
    def _loop():
        _update_loc_prompt()
        _update_presence()

    # Runs on exit.
    @store.mas_submod_utils.functionplugin("exit")
    def _exit():
        if _client is not None:
            _disconnect_client()