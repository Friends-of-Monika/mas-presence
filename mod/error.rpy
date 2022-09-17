init 50 python in fom_presence:

    _ERR_CFG = "cfg"
    _ERR_CON = "con"
    _ERR_ACT = "act"
    _ERR_PIN = "pin"


    class _ErrorContext(object):
        def __init__(self, max_stack=1):
            self._reports = dict()
            self._max_stack = max_stack

        def report(self, _type, message):
            stack = self._reports.get(_type, 0)
            if stack <= self._max_stack or stack < 0:
                renpy.notify(message)

                if _type in self._reports:
                    self._reports[_type] = 0

            self._reports[_type] += 1

        def resolve(self, _type, message=None):
            stack = self._reports.pop(_type, 0)
            if stack > 0 and message is not None:
                renpy.notify(message)


    _ectx_main = _ErrorContext()
    _ectx_opts = _ErrorContext(max_stack=-1)