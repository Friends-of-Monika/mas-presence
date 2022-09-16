default persistent._fom_presence_enable = True

init 90 python in fom_presence:

    import store
    from store import persistent

    import os
    import time

    if PY2:
        import ConfigParser as configparser
    else:
        import configparser


    def _get_conf_dir():
        _file = _get_script_file(fallback="game/Submods/Discord Presence Submod")
        return os.path.join("/".join(_file.split("/")[:-1]), "config")

    config_dir = _get_conf_dir()


    def _get_conf_value(parser, section, value, deserializer=str, default=None):
        try:
            return deserializer(parser.get(section, value, raw=True))
        except (configparser.NoOptionError, configparser.NoSectionError) as e:
            return default

    def _subst_str_provider(s):
        def provide():
            return renpy.substitute(s, _uservars)
        return _Provider(provide)


    _timestamp_type = dict()

    def _dt_to_ts(dt):
        return int(time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0)

    def _parse_ts_provider(s):
        return _timestamp_type.get(s.lower())

    def _ts_none():
        return None
    _timestamp_type["none"] = _Provider(_ts_none)

    def _ts_session_start():
        return _dt_to_ts(persistent.sessions["current_session_start"])
    _timestamp_type["sessionstart"] = _Provider(_ts_session_start)


    class Config(object):
        def __init__(self, parser):
            condition = _get_conf_value(parser, "Presence", "Condition")
            compile(condition, "<string>", "eval")
            self.condition = condition
            self.priority = _get_conf_value(parser, "Presence", "Priority", int)

            self.app_id = _get_conf_value(parser, "Client", "ApplicationID", int)

            self.details = _get_conf_value(parser, "Activity", "Details", _subst_str_provider)
            self.state = _get_conf_value(parser, "Activity", "State", _subst_str_provider)

            self.large_image = _get_conf_value(parser, "Assets", "LargeImage")
            self.large_text = _get_conf_value(parser, "Assets", "LargeText", _subst_str_provider)
            self.small_image = _get_conf_value(parser, "Assets", "SmallImage")
            self.small_text = _get_conf_value(parser, "Assets", "SmallText", _subst_str_provider)

            self.start_ts = _get_conf_value(parser, "Timestamps", "Start", _parse_ts_provider)
            self.stop_ts = _get_conf_value(parser, "Timestamps", "End", _parse_ts_provider)

        @staticmethod
        def load_file(path):
            c = configparser.ConfigParser()
            c.read(path)
            return Config(c)

        @property
        def activity(self):
            a = Activity()

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

            return a


    _configs = list()

    def _load_configs():
        for _dir, _, files in os.walk(config_dir):
            for _file in files:
                try:
                    _configs.append((_file, Config.load_file(os.path.join(_dir, _file))))

                except configparser.ParsingError as e:
                    # TODO: Notify user with a toast message
                    _error("Could not load presence config from file {0}: {1}".format(_file, e))

    def get_active_config():
        active = list()

        for _file, conf in _configs:
            try:
                if bool(eval(conf.condition, _uservars, store.__dict__)):
                    active.append(conf)

            except Exception as e:
                # TODO: Notify user with a toast message
                _error("Could not evaluate presence config condition in file {0}: {1}".format(_file, e))

        if len(active) == 0:
            return None

        active.sort(key=lambda it: it.priority, reverse=True)
        return active[0]