# error.rpy contains error contexts that are used to appropriately display
# error notifications using report/resolve model, once a problem is reported and
# flashed on screen, no new errors cause a flash; on resolve, a message is shown
# and error messages can be shown again.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod


init -90 python in _fom_presence_error:

    import store

    from store import _fom_presence_logging as logging

    import contextlib


    class Context(object):
        """
        Context is a simple error context that contains logger to report errors
        to and sampling info. Contexts are used to keep certain errors sampled
        (e.g. not displayed to user too repeatedly not to create a flashing
        notification effect) or unsampled and to keep them logged to separate
        locations on demand.
        """

        def __init__(self, logger, sample=True):
            """
            Constructs a new Context instance with the provided logger and with
            sampling preference.

            IN:
                logger -> logger:
                    Logger to use in case of error logging.

                sample -> bool, default True:
                    If True, errors will not be repeated unless they are
                    reported and then resolved.
            """

            self._logger = logger
            self._sample = sample

    class Error(object):
        """
        Error represents an error type that can be reported and resolved and
        occurences of which can be tracked and possibly sampled.
        """

        def __init__(
            self,
            log_message_report=None,
            log_message_resolve=None,
            ui_message_report=None,
            ui_message_resolve=None
        ):
            """
            Creates new Error instance with the provided messages (optional.)

            IN:
                log_message_report -> str, default None:
                    Message template for reporting errors in log.

                log_message_resolve -> str, default None:
                    Message template for logging resolved errors.

                ui_message_report -> str, default None:
                    Message template for reporting errors in UI.

                ui_message_resolve -> str, default None:
                    Message template for displaying resolved errors in UI.
            """

            self._log_report=log_message_report
            self._log_resolve=log_message_resolve
            self._ui_report=ui_message_report
            self._ui_resolve=ui_message_resolve
            self._count = 0

        def report(self, *args):
            """
            Reports an error and increases the error occurrence counter by one,
            making further reports silent if sampling is enabled.

            IN:
                *args -> any[]:
                    Arguments to pass to formatting function that will format
                    the message.
            """

            self._count += 1
            self._invoke_msg_func_triples([
                (current_context._logger.error, self._log_report, args),
                (renpy.notify, self._ui_report, args)
            ])

        def resolve(self, *args):
            """
            Resolves an error and resets the error occurence counter, pushing a
            resolve message if error occurence counter was greater than zero.

            IN:
                *args -> any[]:
                    Arguments to pass to formatting function that will format
                    the message.
            """

            if self._count > 0:
                self._count = 0
                self._invoke_msg_func_triples([
                    (current_context._logger.info, self._log_resolve, args),
                    (renpy.notify, self._ui_resolve, args)
                ])

        def _invoke_msg_func_triples(self, input):
            """
            Unpacks parameters of 3-tuples in input parameter and passes them to
            _invoke_with_err_str function if message is not None.

            IN:
                input -> tuple[]:
                    List of 3-tuples:
                        [0]: function to pass formatted message to
                        [1]: message template to format with args
                        [2]: args to pass to [1] message
            """

            for function, message, args in input:
                if message is not None:
                    self._invoke_with_err_str(function, message, *args)

        def _invoke_with_err_str(self, function, message, *args):
            """
            Invokes provided function with formatted message template if
            sampling is disabled or if occurrences counter is zero.

            IN:
                function -> function:
                    Function to pass formatter message to.

                message -> str:
                    Message template to format with args.

                *args -> any[]:
                    Arguments to pass to formatting function.
            """

            if self._count == 0 or not current_context._sample:
                if args is not None:
                    message = message.format(*args)
                function(message)


    MAIN_CONTEXT = Context(logging.DEFAULT)
    OPTIONS_CONTEXT = Context(logging.DEFAULT, sample=False)
    EXTENSIONS_CONTEXT = Context(logging.DEFAULT, sample=False)

    current_context = MAIN_CONTEXT

    @contextlib.contextmanager
    def temporary_context(context):
        """
        Context manager function to temporarily change global error context for
        the desired piece of code.

        IN:
            context -> Context:
                Error context to use for this context manager.
        """

        global current_context
        prev_context, current_context = current_context, context

        try:
            yield
        finally:
            current_context = prev_context