# config.rpy contains classes and functions for working with presence config
# files as well as stores persistent variables affecting the behavior of
# Discord Presence Submod.
#
# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/discord-presence-submod

default persistent._fom_presence_enabled = True


init 90 python in _fom_presence_config:

    import store
    from store import persistent
    from store import _fom_presence as mod
    from store import _fom_presence_discord as discord
    from store import _fom_presence_error as error
    from store import _fom_presence_logging as logging

    import sys
    import os
    import time

    if sys.version_info.major == 2:
        import ConfigParser as configparser
        import io
    else:
        import configparser


    # Errors

    _ERROR_CONFIG_LOADING = error.Error(
        log_message_report="Could not load presence config from file {0}: {1}",
        ui_message_report="Some (or all) Presence Configs are invalid and could not be loaded. They most likely have\n"
                          "invalid syntax or condition, for more details see log/submod_log.log"
    )


    # Supplier and related functions and constructors

    class _Supplier(object):
        def __init__(self, provide_func):
            self._provide = provide_func

        def get(self, *args, **kwargs):
            return self._provide(*args, **kwargs)

    _none_supplier = _Supplier(lambda: None)

    def _substitute_supplier(s):
        def supply():
            return renpy.substitute(s)
        return _Supplier(supply)



    # Timestamps and related functions and variables

    def _datetime_to_int(dt):
        return int(time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0)


    _timestamps_db = dict()
    _timestamps_db["none"] = _none_supplier

    def _parse_ts_supplier(s):
        return _timestamps_db.get(s.lower())

    def _timestamp_session_start():
        return _datetime_to_int(persistent.sessions["current_session_start"])
    _timestamps_db["sessionstart"] = _Supplier(_timestamp_session_start)

    def _timestamp_upcoming_event_1h():
        # NOTE: Discord just won't render timestamps that exceed 1 hour.
        eve = _get_next_event(1)
        if eve is None:
            return None
        if eve[0].total_seconds() > 3600:
            return None
        return int(time.time() + eve[0].total_seconds())
    _timestamps_db["upcomingevent1h"] = _Supplier(_timestamp_upcoming_event_1h)


    # ConfigParser wrapper and related functions and classes

    def _parse_bool(s):
        if s.lower() in ("true", "yes", "y"):
            return True
        return False

    if sys.version_info.major == 2:
        def _open_with_encoding(path, mode, encoding="utf-8"):
            return io.open(path, "r", encoding="utf-8")
    else:
        def _open_with_encoding(path, mode, encoding="utf-8"):
            return open(path, "r", encoding="utf-8")

    class _ParserWrapper(object):
        def __init__(self, parser):
            self._parser = parser

        def get_value(self, section, value, deserializer=str, default=None):
            try:
                return deserializer(self._parser.get(section, value, raw=True))
            except (configparser.NoOptionError, configparser.NoSectionError) as e:
                return default


    # Config object and related functions and variables

    class Config(object):
        def __init__(self, parser):
            condition = parser.get_value("Presence", "Condition")
            compile(condition, "<string>", "eval")
            self.condition = condition

            self.priority = parser.get_value("Presence", "Priority", int, 0)
            self.dynamic = parser.get_value("Presence", "Dynamic", _parse_bool, True)

            self.app_id = parser.get_value("Client", "ApplicationID", int)

            self.details = parser.get_value("Activity", "Details", _substitute_supplier, _none_supplier)
            self.state = parser.get_value("Activity", "State", _substitute_supplier, _none_supplier)

            self.large_image = parser.get_value("Assets", "LargeImage")
            self.large_text = parser.get_value("Assets", "LargeText", _substitute_supplier, _none_supplier)
            self.small_image = parser.get_value("Assets", "SmallImage")
            self.small_text = parser.get_value("Assets", "SmallText", _substitute_supplier, _none_supplier)

            self.start_ts = parser.get_value("Timestamps", "Start", _parse_ts_supplier, _none_supplier)
            self.stop_ts = parser.get_value("Timestamps", "End", _parse_ts_supplier, _none_supplier)

            self._activity = None

        @staticmethod
        def from_file(path):
            c = configparser.ConfigParser()
            with _open_with_encoding(path, "r", encoding="utf-8") as f:
                c.readfp(f, path.replace("\\", "/").split("/")[:-1])
            return Config(_ParserWrapper(c))

        def to_activity(self):
            if self._activity is not None:
                return self._activity

            a = discord.Activity()

            if self.state is not None:
                a.state = self.state.get()
            if self.details is not None:
                a.details = self.details.get()

            if self.start_ts is not None:
                a.timestamps.start = self.start_ts.get()
            if self.stop_ts is not None:
                a.timestamps.end = self.stop_ts.get()

            if self.large_image is not None:
                a.assets.large_image = self.large_image
                if self.large_text is not None:
                    a.assets.large_text = self.large_text.get()
            if self.small_image is not None:
                a.assets.small_image = self.small_image
                if self.small_text is not None:
                    a.assets.small_text = self.small_text.get()

            if not self.dynamic:
                self._activity = a
            return a


    _config_dir = os.path.join(mod.basedir, "config")
    _configs = list()

    def reload_configs():
        del _configs[:]

        for _dir, _, files in os.walk(_config_dir):
            for _file in files:
                if not (
                    _file.endswith(".ini") or
                    _file.endswith(".cfg") or
                    _file.endswith(".conf")
                ):
                    continue

                try:
                    _file = os.path.join(_dir, _file)
                    _configs.append((_file, Config.from_file(_file)))
                except Exception as e:
                    _ERROR_CONFIG_LOADING.report(_file[len(_config_dir) + 1:], e)

    def get_active_config():
        active = list()

        for _file, conf in _configs:
            try:
                if bool(eval(conf.condition, dict(), store.__dict__)):
                    active.append(conf)
            except Exception as e:
                _ERROR_CONFIG_LOADING.report(_file[len(_config_dir) + 1:], e)

        if len(active) == 0:
            return None

        active.sort(key=lambda it: it.priority, reverse=True)
        return active[0]