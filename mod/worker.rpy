# worker.rpy contains a minimal background task executor used to keep blocking
# Discord IPC/RPC communication off the main game thread.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod

init -90 python in _fom_presence_worker:

    # Imports

    import threading
    import collections
    import time
    import traceback

    class Task(object):
        """
        Task is a unit of work executed by Worker on its thread. Once executed,
        it holds either the returned result or the raised error.
        """

        def __init__(self, func, callback=None, key=None):
            """
            Creates a new Task instance.

            IN:
                func -> callable:
                    Function to call on the worker thread with no arguments.

                callback -> callable or None, default None:
                    Function to call on the main thread (from Worker.poll) with
                    this Task as the only argument after func finishes.

                key -> any, default None:
                    Coalescing key. If the last pending task has the same
                    (non-None) key, it is replaced with this one.
            """

            self.func = func
            self.callback = callback
            self.key = key
            self.result = None
            self.error = None
            self.traceback = None
            self.duration = None


    class Worker(object):
        """
        Worker executes submitted tasks one by one, in submission order, on a
        dedicated daemon thread. Results are not delivered by the worker thread
        itself; the main thread must call poll() to run task callbacks so that
        they can safely interact with Ren'Py.

        NOTE:
            Queue module is not available in MAS Python distribution, hence
            the deque guarded with a condition variable.
        """

        def __init__(self, name, logger=None):
            """
            Creates a new Worker instance and starts its thread.

            IN:
                name -> str:
                    Name of the worker thread.

                logger -> logger or None, default None:
                    Logger to report worker thread lifecycle and errors to.
            """

            self._name = name
            self._logger = logger
            self._cond = threading.Condition(threading.Lock())
            self._pending = collections.deque()
            self._done = collections.deque()
            self._started_at = None
            self._stopped = False
            self._cleanup = None

            self._thread = threading.Thread(target=self._run, name=name)
            self._thread.daemon = True
            self._thread.start()

        @property
        def alive(self):
            """
            True if worker thread is still running (it may be stopped, but
            still blocked in a task or cleanup.)
            """

            return self._thread.is_alive()

        @property
        def stopped(self):
            """
            True if this worker no longer accepts tasks.
            """

            return self._stopped

        def submit(self, func, callback=None, key=None):
            """
            Schedules func to be called on the worker thread.

            IN:
                func -> callable:
                    Function to call on the worker thread with no arguments.

                callback -> callable or None, default None:
                    Function to call on the main thread with the finished Task.

                key -> any, default None:
                    Coalescing key; see Task constructor.

            OUT:
                bool:
                    True if task was scheduled, False if worker is stopped.
            """

            task = Task(func, callback, key)
            with self._cond:
                if self._stopped:
                    return False

                if (
                    key is not None
                    and self._pending
                    and self._pending[-1].key == key
                ):
                    self._pending[-1] = task
                else:
                    self._pending.append(task)

                self._cond.notify()
            return True

        def running_for(self):
            """
            Returns for how long the current task has been running.

            OUT:
                float:
                    Seconds since the current task was started.

                None:
                    If no task is currently running.
            """

            started_at = self._started_at
            if started_at is None:
                return None
            return time.time() - started_at

        def poll(self):
            """
            Runs callbacks of finished tasks. Must be called from the main
            thread.
            """

            while True:
                try:
                    task = self._done.popleft()
                except IndexError:
                    break

                if task.callback is not None:
                    task.callback(task)

        def stop(self, cleanup=None, timeout=None):
            """
            Stops this worker: pending tasks are dropped, results of the
            current task (if any) are discarded and cleanup is called on the
            worker thread as soon as the current task finishes, after which
            the thread exits.

            IN:
                cleanup -> callable or None, default None:
                    Function to call on the worker thread before exiting.

                timeout -> float or None, default None:
                    If not None, wait up to this many seconds for the worker
                    thread to exit.
            """

            with self._cond:
                self._stopped = True
                self._pending.clear()
                self._cleanup = cleanup
                self._cond.notify()

            if timeout is not None:
                self._thread.join(timeout)

        def _run(self):
            """
            Worker thread main loop.
            """

            self._log("debug", "Worker thread {0} started.".format(self._name))

            while True:
                with self._cond:
                    while not self._pending and not self._stopped:
                        self._cond.wait()

                    if self._stopped:
                        cleanup = self._cleanup
                        break

                    task = self._pending.popleft()
                    self._started_at = time.time()

                try:
                    task.result = task.func()
                except Exception as e:
                    task.error = e
                    task.traceback = traceback.format_exc()

                with self._cond:
                    task.duration = time.time() - self._started_at
                    self._started_at = None
                    if not self._stopped:
                        self._done.append(task)

            if cleanup is not None:
                try:
                    cleanup()
                except Exception:
                    self._log("error", "Worker thread {0} cleanup failed:\n{1}".format(self._name, traceback.format_exc()))

            self._log("debug", "Worker thread {0} exited.".format(self._name))

        def _log(self, level, message):
            """
            Logs message with the provided level if logger is set.

            IN:
                level -> str:
                    Name of logger method to call (debug, info, etc.)

                message -> str:
                    Message to log.
            """

            if self._logger is not None:
                getattr(self._logger, level)(message)
