init 50 python in fom_presence:

    _ERR_CFG = "cfg"
    _ERR_CON = "con"
    _ERR_ACT = "act"
    _ERR_PIN = "pin"


    class _ErrorContext(object):
        def __init__(self, stack=False):
            self._reports = dict()
            self._stack = stack

        def report(self, _type, message):
            if _type not in self._reports or self._stack:
                renpy.notify(message)
                self._reports[_type] = 1

            else:
                self._reports[_type] += 1

        def resolve(self, _type, message):
            if self._reports.pop(_type, None):
                renpy.notify(message)


    _ectx_main = _ErrorContext()
    _ectx_opts = _ErrorContext(stack=True)