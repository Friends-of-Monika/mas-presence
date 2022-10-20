# This Ren'Py script exists to provide custom variables framework that allows
# registration of custom variables or variable sets in a convenient way.
#
# Author: Herman S. <dreamscache.d@gmail.com>
# Since: 0.0.1
#
# Functions:
#   cvars_add_var(name, supplier, loop=True) - register custom variable (or
#     function that can be used in condition expressions or interpolations with
#     name <name> and supplier function <supplier> that must take no arguments
#     and must return value of this variable. If <loop> is True, then this
#     variable will be updated on each loop and not just on startup.
#   cvars_add_var_set(supplier, loop=True) - register custom variables set that
#     is returned from <supplier> function that must take no arguments as
#     dictionary of string keys and any type of values that correspond to custom
#     variables names and values. If <loop> is True, then this variable set will
#     be updated on each loop and not just on startup.
#
# Extensions relying on this extension must have init offset of value greater
# than 100.

init 100 python in fom_presence_extensions:

    import store
    from store import _fom_presence_logging as logging
    from store import _fom_presence_error as error

    _ERROR_VAR_UPDATING = error.Error(
        log_message_report=(
            "[Custom Variables] Could not update custom variable {0}: {1}"
        )
    )


    _CVARS_SINGLE = 0
    _CVARS_SET = 1

    _cvars = list()


    def cvars_add_var(name, supplier, loop=True):
        _cvars.append((_CVARS_SINGLE, name, supplier, loop))

    def cvars_add_var_set(supplier, loop=True):
        _cvars.append((_CVARS_SET, None, supplier, loop))

    def _cvars_export_var(name, value):
        setattr(store, name, value)

    def _cvars_export_var_set(values):
        for name, value in values.items():
            setattr(store, name, value)

    def _cvars_update_vars(loop):
        for _type, name, supplier, allow_loop in _cvars:
            if loop and not allow_loop:
                continue

            try:
                if _type == _CVARS_SINGLE:
                    _cvars_export_var(name, supplier())
                elif _type == _CVARS_SET:
                    _cvars_export_var_set(supplier())

            except Exception as e:
                with error.temporary_context(error.EXTENSIONS_CONTEXT):
                    _ERROR_VAR_UPDATING.report(name, e)


    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=10)
    def _cvars_update_preloop():
        _cvars_update_vars(loop=False)


    @store.mas_submod_utils.functionplugin("ch30_loop", priority=10)
    def _cvars_update_loop():
        _cvars_update_vars(loop=True)