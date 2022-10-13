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

        def __init__(self, logger, sample=True):
            self._logger = logger
            self._sample = sample

    class Error(object):

        def __init__(
            self,
            log_message_report=None,
            log_message_resolve=None,
            ui_message_report=None,
            ui_message_resolve=None
        ):
            self._log_report=log_message_report
            self._log_resolve=log_message_resolve
            self._ui_report=ui_message_report
            self._ui_resolve=ui_message_resolve
            self._count = 0

        def report(self, *args):
            self._count += 1
            self._invoke_msg_func_triples([
                (current_context._logger.error, self._log_report, args),
                (renpy.notify, self._ui_report, args)
            ])

        def resolve(self, *args):
            if self._count > 0:
                self._count = 0
                self._invoke_msg_func_triples([
                    (current_context._logger.info, self._log_resolve, args),
                    (renpy.notify, self._ui_resolve, args)
                ])

        def _invoke_msg_func_triples(self, input):
            for function, message, args in input:
                if message is not None:
                    self._invoke_with_err_str(function, message, *args)

        def _invoke_with_err_str(self, function, message, *args):
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
        global current_context
        prev_context, current_context = current_context, context

        try:
            yield
        finally:
            current_context = prev_context