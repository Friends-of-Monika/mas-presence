# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/mas-presence

init 100 python in _fom_presence:
    import store
    from store import persistent

    from store import _fom_presence_config as config
    from store import _fom_presence_error as error
    from store import _fom_presence_discord as discord
    from store import _fom_presence_logging as logging
    from store import _fom_presence_worker as worker

    import socket
    import datetime
    import traceback
    import time

    _TIMEOUT_LOCK_DURATION = datetime.timedelta(seconds=45)

    # Time after which a Discord call still in progress is considered hung and
    # its worker is abandoned. Socket and pipe reads time out on their own well
    # before that, but reads from Windows named pipes may block indefinitely
    # if PeekNamedPipe could not be loaded.
    _HANG_TIMEOUT = 20

    # Maximum amount of abandoned workers still stuck in a blocking call before
    # no new connection attempts are made.
    _MAX_STUCK_WORKERS = 3

    # Time to wait for the worker to disconnect cleanly on exit.
    _EXIT_TIMEOUT = 2

    # Minimum interval between processing Discord results from Ren'Py periodic
    # callback (which itself is invoked approximately 20 times a second.)
    _POLL_INTERVAL = 1


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

    _ERROR_CLIENT_HUNG = error.Error(
        log_message_report="Discord did not respond in {0} seconds, abandoning connection.",
        log_message_resolve="Connection with Discord established.",
        ui_message_report="Discord is not responding, further attempts will be possible in {0} seconds.".format(int(_TIMEOUT_LOCK_DURATION.total_seconds())),
        ui_message_resolve="Connection with Discord established."
    )

    _ERROR_CLIENT_LOST = error.Error(
        log_message_report="Connection with Discord lost: {0}.",
        log_message_resolve="Re-established connection with Discord.",
        ui_message_report="Connection with Discord lost. Trying to re-establish it...",
        ui_message_resolve="Connection with Discord re-established."
    )

    _ERROR_CLIENT_ACTIVITY = error.Error(
        log_message_report="Could not set activity: {0}",
        ui_message_report="Could not set Rich Presence activity."
    )


    class _Outcome(object):
        """
        Outcome collects effects of a session operation performed on the worker
        thread so that they can be applied later on the main thread.
        """

        def __init__(self):
            self.errors = []
            self.connected = None
            self.timeout_lock = None

        def report(self, err, *args):
            self.errors.append((err.report, args))

        def resolve(self, err, *args):
            self.errors.append((err.resolve, args))


    class _Session(object):
        """
        Session owns Discord RPC clients and performs all (blocking) socket
        communication. Its methods must only be called on the worker thread.
        """

        def __init__(self):
            self._clients = dict()
            self._active_app_id = None

        def connect(self, app_id, activity):
            outcome = _Outcome()
            self._show(app_id, activity, outcome)
            return outcome

        def update(self, app_id, activity):
            outcome = _Outcome()
            self._show(app_id, activity, outcome)
            return outcome

        def disconnect(self):
            for client in self._clients.values():
                try:
                    client.disconnect()
                except (IOError, OSError):
                    pass

            self._clients.clear()
            self._active_app_id = None

        def _show(self, app_id, activity, outcome):
            if self._active_app_id is not None and self._active_app_id != app_id:
                prev_client = self._clients.get(self._active_app_id)
                self._active_app_id = None
                if prev_client is not None:
                    try:
                        prev_client.clear_activity()
                    except discord.ProtocolError as e:
                        self._lose_connection(e, outcome)
                        return
                    except discord.CallError as e:
                        outcome.report(_ERROR_CLIENT_ACTIVITY, e)

            if app_id is None:
                return

            client = self._get_or_connect_client(app_id, outcome)
            if client is None:
                return
            outcome.connected = True

            try:
                client.set_activity(activity)
                self._active_app_id = app_id
                outcome.resolve(_ERROR_CLIENT_ACTIVITY)
                outcome.resolve(_ERROR_CLIENT_LOST)
            except discord.ProtocolError as e:
                self._lose_connection(e, outcome)
            except discord.CallError as e:
                outcome.report(_ERROR_CLIENT_ACTIVITY, e)

        def _lose_connection(self, e, outcome):
            # Connection is unusable now (and may be out of sync if it timed
            # out), so drop all clients; presence will reconnect on next loop.
            outcome.report(_ERROR_CLIENT_LOST, e)
            self.disconnect()
            outcome.connected = False

        def _get_or_connect_client(self, app_id, outcome):
            client = self._clients.get(app_id)
            if client is not None:
                return client

            rpc_socket = self._connect_socket(outcome)
            if rpc_socket is None:
                return None

            try:
                client = discord.Client(rpc_socket)
                client.handshake(app_id)
                outcome.resolve(_ERROR_CLIENT_TIMEOUT)
                outcome.resolve(_ERROR_CLIENT_HUNG)
                outcome.resolve(_ERROR_CLIENT_CONNECTION)
                outcome.timeout_lock = False
            except (discord.ProtocolError, discord.CallError) as e:
                try:
                    rpc_socket.close()
                except (IOError, OSError):
                    pass

                if isinstance(e, discord.ProtocolError) and isinstance(e.args[0], socket.timeout):
                    outcome.report(_ERROR_CLIENT_TIMEOUT)
                    outcome.timeout_lock = True
                else:
                    outcome.report(_ERROR_CLIENT_CONNECTION, e)
                return None

            self._clients[app_id] = client
            return client

        def _connect_socket(self, outcome):
            try:
                rpc_socket = discord.get_rpc_socket()
            except socket.timeout:
                outcome.timeout_lock = True
                outcome.report(_ERROR_CLIENT_TIMEOUT)
                return None
            except (IOError, OSError) as e:
                outcome.report(_ERROR_CLIENT_CONNECTION, e)
                return None

            if rpc_socket is None:
                outcome.report(_ERROR_SOCKET_NOT_FOUND)
                return None

            outcome.resolve(_ERROR_SOCKET_NOT_FOUND)
            outcome.resolve(_ERROR_CLIENT_TIMEOUT)
            outcome.timeout_lock = False
            return rpc_socket


    class _PresenceController(object):
        """
        Presence controller keeps main thread state of the presence and
        delegates all communication with Discord to a worker thread, applying
        its results on the main thread in poll().
        """

        def __init__(self, logger):
            self._logger = logger
            self._connected = False
            self._connecting = False
            self._config = None
            self._lock_conn_until = None
            self._last_mean_update = None
            self._worker = None
            self._session = None
            self._stuck_workers = []

            # Incremented on every disconnect so that results of operations
            # submitted before it do not mark presence as connected again.
            self._epoch = 0

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
            if self._connecting:
                self._logger.debug("Not connecting to Discord: connection attempt already in progress.")
                return
            if self.timeout_locked:
                self._logger.debug("Not connecting to Discord: connection attempts locked until {0}.".format(self._lock_conn_until))
                return

            if self._config is None:
                self._config = config.get_active_config()
                if self._config is None:
                    self._logger.debug("Not connecting to Discord: no active config.")
                    return

            if self._submit("connect", self._config):
                self._connecting = True

        def disconnect(self):
            self._logger.debug("Disconnecting from Discord.")
            self._epoch += 1
            self._connected = False
            self._connecting = False

            if self._worker is not None:
                self._worker.submit(self._session.disconnect)

        def update(self, with_config=None):
            if with_config is None:
                with_config = config.get_active_config()

            prev_config, self._config = self._config, with_config
            if self._config is not None and (prev_config is None or prev_config != self._config):
                self._last_mean_update = datetime.datetime.now()

            self._submit("update", self._config, key="update")

        def poll(self):
            """
            Applies results of finished Discord operations and abandons the
            worker if it got stuck. Must be called from the main thread.
            """

            if self._worker is None:
                return

            self._worker.poll()

            elapsed = self._worker.running_for()
            if elapsed is not None and elapsed > _HANG_TIMEOUT:
                self._abandon_worker(elapsed)

        def shutdown(self):
            """
            Disconnects and stops the worker, waiting for it to finish.
            """

            self._epoch += 1
            self._connected = False
            self._connecting = False

            if self._worker is not None:
                self._logger.debug("Shutting down Discord worker.")
                self._worker.stop(cleanup=self._session.disconnect, timeout=_EXIT_TIMEOUT)
                if self._worker.alive:
                    self._logger.warning("Discord worker did not finish in {0}s, leaving it behind.".format(_EXIT_TIMEOUT))
                self._worker = None
                self._session = None

        def _submit(self, op, with_config, key=None):
            if not self._ensure_worker():
                return False

            app_id, activity = None, None
            if with_config is not None:
                app_id, activity = with_config.app_id, with_config.to_activity()

            func = getattr(self._session, op)
            context = error.current_context
            epoch = self._epoch

            if logging.TRACE:
                self._logger.debug("Submitting {0} (app ID {1}.)".format(op, app_id))

            return self._worker.submit(
                lambda: func(app_id, activity),
                lambda task: self._on_done(task, op, context, epoch),
                key=key
            )

        def _on_done(self, task, op, context, epoch):
            current = epoch == self._epoch
            if current and op == "connect":
                self._connecting = False

            if task.error is not None:
                self._logger.error("Unexpected error while communicating with Discord ({0}):\n{1}".format(op, task.traceback))
                return

            outcome = task.result
            if logging.TRACE:
                self._logger.debug("Finished {0} in {1:.3f}s (connected: {2}, timeout lock: {3}, current: {4}.)".format(
                    op, task.duration, outcome.connected, outcome.timeout_lock, current
                ))
            with error.temporary_context(context):
                for func, args in outcome.errors:
                    func(*args)

            if outcome.timeout_lock is not None:
                self._set_timeout_lock(outcome.timeout_lock)

            if current and outcome.connected is not None and outcome.connected != self._connected:
                self._logger.debug("Discord presence is now {0}.".format("connected" if outcome.connected else "disconnected"))
                self._connected = outcome.connected
                renpy.restart_interaction()

        def _ensure_worker(self):
            if self._worker is not None:
                return True

            self._stuck_workers = [w for w in self._stuck_workers if w.alive]
            if len(self._stuck_workers) >= _MAX_STUCK_WORKERS:
                self._logger.warning("Too many Discord connections are still not responding, not connecting.")
                self._set_timeout_lock(True)
                return False

            self._worker = worker.Worker("fom_presence_discord", self._logger)
            self._session = _Session()
            return True

        def _abandon_worker(self, elapsed):
            # The stuck call cannot be interrupted (and closing a Windows pipe
            # from another thread may block as well), so let the worker thread
            # clean up after itself if it ever unblocks and start over.
            self._logger.warning("Discord worker stuck in a call for {0:.1f}s, abandoning it ({1} abandoned before.)".format(
                elapsed, len(self._stuck_workers)
            ))

            self._worker.stop(cleanup=self._session.disconnect)
            self._stuck_workers.append(self._worker)
            self._worker = None
            self._session = None

            self._epoch += 1
            self._connected = False
            self._connecting = False

            _ERROR_CLIENT_HUNG.report(_HANG_TIMEOUT)
            self._set_timeout_lock(True)
            renpy.restart_interaction()

        def _set_timeout_lock(self, lock):
            if lock:
                self._logger.debug("Locking connection attempts for {0}s.".format(int(_TIMEOUT_LOCK_DURATION.total_seconds())))
                self._lock_conn_until = datetime.datetime.now() + _TIMEOUT_LOCK_DURATION
            else:
                self._lock_conn_until = None


    presence = _PresenceController(logging.DEFAULT)


    _last_periodic_poll = 0

    # Runs on the main thread approximately 20 times a second, but only polls
    # once per _POLL_INTERVAL seconds.
    def _on_periodic():
        global _last_periodic_poll

        now = time.time()
        if now - _last_periodic_poll < _POLL_INTERVAL:
            return
        _last_periodic_poll = now

        try:
            presence.poll()
        except Exception:
            logging.DEFAULT.error("Failed to process Discord presence results:\n{0}".format(traceback.format_exc()))

    if hasattr(renpy.config, "periodic_callbacks"):
        renpy.config.periodic_callbacks.append(_on_periodic)
    else:
        logging.DEFAULT.warning("Ren'Py periodic callbacks are not available, Discord results will only be processed every few seconds.")


    # Runs once on startup, but post-init.
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=100)
    def on_preloop():
        logging.DEFAULT.debug("Starting up (presence enabled: {0}.)".format(persistent._fom_presence_enabled))
        if persistent._fom_presence_enabled:
            config.reload_configs()
        if not presence.timeout_locked:
            presence.connect()


    # Runs approximately once per 5 seconds while not in dialogue.
    @store.mas_submod_utils.functionplugin("ch30_loop", priority=100)
    def on_loop():
        presence.poll()
        if persistent._fom_presence_enabled:
            if presence.connected:
                presence.update()
            elif not presence.timeout_locked:
                presence.connect()


    # Runs when an event is called.
    @store.mas_submod_utils.functionplugin("call_next_event", priority=100)
    def on_event():
        on_loop()


    # Runs on exit.
    @store.mas_submod_utils.functionplugin("exit", priority=100)
    def on_exit():
        presence.shutdown()
