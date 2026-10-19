# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/mas-presence

init 100 python in _fom_presence:
    import store
    from store import persistent

    from store import _fom_presence_config as config
    from store import _fom_presence_status as status
    from store import _fom_presence_discord as discord
    from store import _fom_presence_logging as logging
    from store import _fom_presence_worker as worker

    import socket
    import datetime
    import traceback
    import time
    import math
    import json

    # Connection attempts are locked after timeouts and hangs with exponential
    # backoff: lock duration starts at _BACKOFF_MIN seconds, doubles on each
    # consecutive failure up to _BACKOFF_MAX seconds, and resets once a
    # connection is established.
    _BACKOFF_MIN = 5
    _BACKOFF_MAX = 60

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

    # Minimum interval between automatic connection attempts while not
    # connected (on top of timeout lock.)
    _RETRY_INTERVAL = 5

    # Unchanged activity is not resent to Discord, except once it has been
    # set for this many seconds: since nothing else is sent while connected,
    # this also detects connections lost (e.g. when Discord was restarted.)
    _REFRESH_INTERVAL = 60


    # Keys of problems shown in settings pane (see status.rpy.)
    _STATUS_CONNECTION = "connection"
    _STATUS_ACTIVITY = "activity"


    def _hash_activity(app_id, activity):
        """
        Computes hash of activity as it would be sent to Discord, so that
        unchanged activities can be detected without keeping their copies.

        IN:
            app_id -> int or None:
                Application ID the activity is set for.

            activity -> discord.Activity or None:
                Activity to hash.

        OUT:
            int:
                Hash of application ID and activity.
        """

        data = activity.to_dict() if activity is not None else None
        return hash((app_id, json.dumps(data, sort_keys=True)))


    class _Outcome(object):
        """
        Outcome collects effects of a session operation performed on the worker
        thread so that they can be applied later on the main thread.
        """

        def __init__(self):
            self.status = []
            self.connected = None
            self.timeout_lock = None
            self.activity_set = False

        def set_status(self, key, ui_message, log_message=None, level=status.ERROR):
            self.status.append((status.set, (key, ui_message, log_message, level)))

        def clear_status(self, key, log_message=None):
            self.status.append((status.clear, (key, log_message)))

        def connection_established(self):
            self.clear_status(_STATUS_CONNECTION, "Connection with Discord established.")

        def activity_failed(self, e):
            self.set_status(
                _STATUS_ACTIVITY,
                "Could not set Rich Presence activity, see log/submod_log.log.",
                "Could not set activity: {0}.".format(e)
            )


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
                        outcome.activity_failed(e)

            if app_id is None:
                return

            client = self._get_or_connect_client(app_id, outcome)
            if client is None:
                return
            outcome.connected = True

            try:
                client.set_activity(activity)
                self._active_app_id = app_id
                outcome.activity_set = True
                outcome.clear_status(_STATUS_ACTIVITY)
                outcome.connection_established()
            except discord.ProtocolError as e:
                self._lose_connection(e, outcome)
            except discord.CallError as e:
                outcome.activity_failed(e)

        def _lose_connection(self, e, outcome):
            # Connection is unusable now (and may be out of sync if it timed
            # out), so drop all clients; presence will reconnect on next loop.
            outcome.set_status(
                _STATUS_CONNECTION,
                "Connection with Discord lost.",
                "Connection with Discord lost: {0}.".format(e)
            )
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
                outcome.connection_established()
                outcome.timeout_lock = False
            except (discord.ProtocolError, discord.CallError) as e:
                try:
                    rpc_socket.close()
                except (IOError, OSError):
                    pass

                if isinstance(e, discord.ProtocolError) and isinstance(e.args[0], socket.timeout):
                    self._timed_out(outcome)
                else:
                    self._connection_failed(e, outcome)
                return None

            self._clients[app_id] = client
            return client

        def _connect_socket(self, outcome):
            try:
                rpc_socket = discord.get_rpc_socket()
            except socket.timeout:
                self._timed_out(outcome)
                return None
            except (IOError, OSError) as e:
                self._connection_failed(e, outcome)
                return None

            if rpc_socket is None:
                outcome.set_status(
                    _STATUS_CONNECTION,
                    "Discord is not running (desktop app is required.)",
                    "Could not connect to Discord Rich Presence. Is Discord running locally (not in browser?)",
                    status.WARNING
                )
                return None

            return rpc_socket

        def _timed_out(self, outcome):
            outcome.set_status(
                _STATUS_CONNECTION,
                "Connection with Discord timed out.",
                "Timed out while connecting to Discord RPC."
            )
            outcome.timeout_lock = True

        def _connection_failed(self, e, outcome):
            outcome.set_status(
                _STATUS_CONNECTION,
                "Could not connect to Discord.",
                "Could not connect to Discord RPC: {0}.".format(e)
            )


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
            self._lock_failures = 0
            self._last_attempt = None

            # Hashes of activity last set in Discord and of activity submitted
            # but not yet set, used to skip updates that would change nothing.
            self._sent_hash = None
            self._sent_at = None
            self._pending_hash = None
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
        def connecting(self):
            return self._connecting

        @property
        def timeout_locked(self):
            return self._lock_conn_until is not None and self._lock_conn_until > datetime.datetime.now()

        @property
        def retry_in(self):
            """
            Seconds (rounded up) until next automatic connection attempt, zero
            if it is due, or None if connected or connecting.
            """

            if self._connected or self._connecting:
                return None

            remaining = 0
            if self._last_attempt is not None:
                remaining = _RETRY_INTERVAL - (time.time() - self._last_attempt)
            if self.timeout_locked:
                remaining = max(remaining, (self._lock_conn_until - datetime.datetime.now()).total_seconds())
            return max(0, int(math.ceil(remaining)))

        def reconnect_if_due(self):
            """
            Starts a connection attempt if not connected and retry interval and
            timeout lock have elapsed.
            """

            if self.retry_in == 0:
                self.connect()

        @property
        def last_meaningful_update(self):
            return self._last_mean_update

        def connect(self):
            self._last_attempt = time.time()
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
            self._sent_hash = None
            self._sent_at = None
            self._pending_hash = None
            self._connected = False
            self._connecting = False

            status.clear(_STATUS_CONNECTION)
            status.clear(_STATUS_ACTIVITY)

            if self._worker is not None:
                self._worker.submit(self._session.disconnect)

        def update(self, with_config=None, force=False):
            """
            Updates activity from the provided (or currently active) config.
            Unless forced, nothing is sent if the activity is the same as the
            one already set (or about to be set) in Discord.
            """

            if with_config is None:
                with_config = config.get_active_config()

            # Configs are compared by file, since reloading configs creates new
            # Config instances even for configs that did not change.
            prev_config, self._config = self._config, with_config
            if self._config is not None and (prev_config is None or prev_config.file != self._config.file):
                self._last_mean_update = datetime.datetime.now()

            self._submit("update", self._config, key="update", force=force)

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
            self._sent_hash = None
            self._sent_at = None
            self._pending_hash = None
            self._connected = False
            self._connecting = False

            if self._worker is not None:
                self._logger.debug("Shutting down Discord worker.")
                self._worker.stop(cleanup=self._session.disconnect, timeout=_EXIT_TIMEOUT)
                if self._worker.alive:
                    self._logger.warning("Discord worker did not finish in {0}s, leaving it behind.".format(_EXIT_TIMEOUT))
                self._worker = None
                self._session = None

        def _submit(self, op, with_config, key=None, force=False):
            app_id, activity = None, None
            if with_config is not None:
                app_id, activity = with_config.app_id, with_config.to_activity()

            activity_hash = _hash_activity(app_id, activity)
            fresh = self._sent_at is not None and time.time() - self._sent_at < _REFRESH_INTERVAL
            if op == "update" and not force and (
                activity_hash == self._pending_hash
                or (activity_hash == self._sent_hash and fresh)
            ):
                if logging.TRACE:
                    self._logger.debug("Not submitting {0}: activity unchanged (app ID {1}.)".format(op, app_id))
                return False

            if not self._ensure_worker():
                return False

            func = getattr(self._session, op)
            epoch = self._epoch

            if logging.TRACE:
                self._logger.debug("Submitting {0} (app ID {1}.)".format(op, app_id))

            submitted = self._worker.submit(
                lambda: func(app_id, activity),
                lambda task: self._on_done(task, op, epoch, activity_hash),
                key=key
            )
            if submitted:
                self._pending_hash = activity_hash
            return submitted

        def _on_done(self, task, op, epoch, activity_hash):
            current = epoch == self._epoch
            if current and op == "connect":
                self._connecting = False
                renpy.restart_interaction()

            if current:
                if self._pending_hash == activity_hash:
                    self._pending_hash = None

                # Remember what Discord shows now; on failure forget it, so
                # that the next update is sent regardless.
                outcome = task.result if task.error is None else None
                if outcome is not None and outcome.activity_set:
                    self._sent_hash, self._sent_at = activity_hash, time.time()
                else:
                    self._sent_hash, self._sent_at = None, None

            if task.error is not None:
                self._logger.error("Unexpected error while communicating with Discord ({0}):\n{1}".format(op, task.traceback))
                return

            outcome = task.result
            if logging.TRACE:
                self._logger.debug("Finished {0} in {1:.3f}s (connected: {2}, timeout lock: {3}, current: {4}.)".format(
                    op, task.duration, outcome.connected, outcome.timeout_lock, current
                ))

            # Status of operations submitted before last disconnect is stale.
            if current:
                for func, args in outcome.status:
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
            self._sent_hash = None
            self._sent_at = None
            self._pending_hash = None
            self._connected = False
            self._connecting = False

            status.set(
                _STATUS_CONNECTION,
                "Discord is not responding.",
                "Discord did not respond in {0} seconds, abandoning connection.".format(_HANG_TIMEOUT)
            )
            self._set_timeout_lock(True)
            renpy.restart_interaction()

        def _set_timeout_lock(self, lock):
            if lock:
                duration = min(_BACKOFF_MIN * 2 ** min(self._lock_failures, 16), _BACKOFF_MAX)
                self._lock_failures += 1
                self._logger.debug("Locking connection attempts for {0}s ({1} consecutive failures.)".format(duration, self._lock_failures))
                self._lock_conn_until = datetime.datetime.now() + datetime.timedelta(seconds=duration)
            else:
                self._lock_failures = 0
                self._lock_conn_until = None


    presence = _PresenceController(logging.DEFAULT)


    _last_periodic_poll = 0

    # Set once configs are loaded on first ch30_loop; configs (and store
    # variables their conditions depend on) are not ready before that.
    _ready = False

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
            if _ready and persistent._fom_presence_enabled:
                presence.reconnect_if_due()
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


    def _load_on_first_loop():
        """
        Loads configs once MAS (and other submods) finished starting up, so
        that conditions evaluated on load see all store variables they need.
        Configs are loaded even if presence is disabled, so that they are ready
        once it gets enabled in settings.
        """

        global _ready
        if _ready:
            return
        _ready = True

        logging.DEFAULT.debug("Loading presence configs on first loop.")
        config.reload_configs()


    # Runs approximately once per 5 seconds while not in dialogue.
    @store.mas_submod_utils.functionplugin("ch30_loop", priority=100)
    def on_loop():
        _load_on_first_loop()
        presence.poll()
        if persistent._fom_presence_enabled:
            if presence.connected:
                presence.update()
            else:
                presence.reconnect_if_due()


    # Runs when an event is called.
    @store.mas_submod_utils.functionplugin("call_next_event", priority=100)
    def on_event():
        # Events before first loop (if any) are not presence-worthy yet.
        if _ready:
            on_loop()


    # Runs on exit.
    @store.mas_submod_utils.functionplugin("exit", priority=100)
    def on_exit():
        presence.shutdown()
