# This Ren'Py script exists to provide current topic event label as
# custom variable usable in condition expressions and interpolations.
#
# Author: Herman S. <dreamscache.d@gmail.com>
# Since: 0.3.0
#
# Variables:
#   event_label - current topic label

init 200 python in fom_presence_extensions:

    import store

    from store import MASEventList
    from store.evhand import EventListItem
    from store import _fom_presence

    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=20)
    def _fom_ch30_loop():
        _cvars_export_var("event_label", None)

    @store.mas_submod_utils.functionplugin("call_next_event", priority=20)
    def _fom_call_next_event():
        item = MASEventList.peek()
        if item is None:
            value = None
        else:
            value = item._eli[EventListItem.IDX_EVENT_LABEL]
        _cvars_export_var("event_label", value)
        _fom_presence.on_loop()

    @store.mas_submod_utils.functionplugin("ch30_loop", priority=20)
    def _fom_ch30_loop():
        _cvars_export_var("event_label", None)