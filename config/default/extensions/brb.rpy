# This Ren'Py script exists to provide current be right back event label as
# custom variable usable in condition expressions and interpolations.
#
# Author: Herman S. <dreamscache.d@gmail.com>
# Since: 0.2.0
#
# Variables:
#   brb_label - current be right back label

init 200 python in fom_presence_extensions:

    import store

    from store import mas_idle_mailbox


    def _fom_brb_label():
        return mas_idle_mailbox.read(MASIdleMailbox.IDLE_MODE_CB_LABEL)

    cvars_add_var("brb_label", _fom_brb_label)