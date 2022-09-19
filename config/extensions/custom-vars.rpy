init 100 python in fom_presence_extensions:

    import store
    from store import fom_presence

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
                fom_presence._error((
                    "[Custom Variables] Could not update custom variable {0}: "
                    "{1}"
                ).format(name, e))


    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-10)
    def _cvars_update_preloop():
        _cvars_update_vars(loop=False)


    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-10)
    def update_user_vars():
        _cvars_update_vars(loop=True)