# This Ren'Py script exists to provide additional timestamps to config.
#
# Author: Herman S. <dreamscache.d@gmail.com>
# Since: 0.4.0

init 190 python in fom_presence_extensions:

    import store

    from store import _fom_presence_config as config
    from store import _fom_presence_util as util
    from store import mas_calendar, mas_getEV

    import datetime


    _fom_events_ignored = list()


    def events_ignore(key):
        _fom_events_ignored.append(key)


    def _fom_get_next_event(n_days):
        """
        Finds the closest calendar event within next N days. If none found,
        returns None.

        IN:
            n_days -> int:
                Amount of days to scan for upcoming events.

        OUT:
            Tuple of the following items:
                [0]: amount of days until upcoming event
                [1]: event prompt
                [2]: event key
                [3]: event starting date

            None:
                If no upcoming events were found.
        """

        events = list()

        cur = datetime.date.today()
        for i in range(n_days):
            ev_dict = mas_calendar.calendar_database[cur.month][cur.day]
            for ev_key, ev_tup in ev_dict.items():
                if ev_key in _fom_events_ignored:
                    continue

                if ev_tup[0] == mas_calendar.CAL_TYPE_EV:
                    ev = mas_getEV(ev_key)
                    prompt = ev.prompt
                    years = ev.years
                    sd = ev.start_date

                    if sd is not None and sd < datetime.datetime.now():
                        continue

                else:
                    prompt = ev_tup[1]
                    years = ev_tup[2]
                    sd = datetime.datetime.min

                if years is None or len(years) == 0 or cur.year in years:
                    events.append((cur - datetime.date.today(), prompt, ev_key, sd))

            cur += datetime.timedelta(days=1)

        if len(events) == 0:
            return None

        events.sort(key=lambda it: it[3])
        return events[0]


    def _fom_timestamp_upcoming_event_1h():
        """
        Supplier that provides upcoming event timestamp.

        OUT:
            int:
                Unix timestamp of an upcoming event.

        NOTE:
            Due to Discord limitations regarding timestamps in activity, this
            supplier does not return timestamps for events that are further than
            one hour ahead.
        """

        # NOTE: Discord just won't render timestamps that exceed 1 hour.
        eve = _fom_get_next_event(1, _fom_events_ignored)
        if eve is None:
            return None
        if eve[0].total_seconds() > 3600:
            return None
        return int(time.time() + eve[0].total_seconds())
    config.timestamps_db["upcomingevent1h"] = util.Supplier(_fom_timestamp_upcoming_event_1h)


