# error.rpy contains error contexts that are used to appropriately display
# error notifications using report/resolve model, once a problem is reported and
# flashed on screen, no new errors cause a flash; on resolve, a message is shown
# and error messages can be shown again.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod


init -90 python in fom_presence_error:

    import store.fom_presence_logging as log


    class ErrorContext(object):
        def __init__(self, logger):
            self._logger = logger
            self._errors = dict()

        def get_error(
            self,
            key,
            log_message_report=None,
            log_message_resolve=None,
            ui_message_report=None,
            ui_message_resolve=None,
            sample=True
        ):
            error = self._errors.get(key)
            if error is not None:
                return error

            error = _Error(
                self,
                log_message_report,
                log_message_resolve,
                ui_message_report,
                ui_message_resolve,
                sample
            )
            self._errors[key] = error
            return error

    class _Error(object):
        def __init__(
            self,
            context,
            log_message_report=None,
            log_message_resolve=None,
            ui_message_report=None,
            ui_message_resolve=None,
            sample=True
        ):
            self._context = context
            self._log_report=None,
            self._log_resolve=None,
            self._ui_report=None,
            self._ui_resolve=None,
            self._sample = sample
            self._count = 0

        def report(self, args=None):
            self._count += 1
            self._invoke_msg_func_triples([
                (self._context._logger.error, self._log_report, args),
                (renpy.notify, self._ui_report, args)
            ])

        def resolve(self, args=None):
            self._count = 0
            self._invoke_msg_func_triples([
                (self._context._logger.info, self._log_resolve, args),
                (renpy.notify, self._ui_resolve, args)
            ])

        def _invoke_msg_func_triples(self, input):
            for function, message, args in input:
                if message is not None:
                    self._invoke_with_err_str(function, message, args)

        def _invoke_with_err_str(self, function, message, args=None):
            if self._count == 0 or not self._sample:
                if args is not None:
                    message = message.format(*args)
                function(message)