init -100 python in fom_presence:

    import store
    from store import persistent

    import os
    import time

    if PY2:
        import ConfigParser as configparser
    else:
        import configparser


    def _get_script_file(fallback=None, relative=False):
        """
        Uses internal Ren'Py function renpy.get_filename_line() to locate
        current script file and get its location, accounting for potential
        erroneous outputs produced by this function.

        IN:
            fallback -> str, default None:
                Path to use as a fallback in case this function fails to find
                appropriate current script location.

            relative -> bool, default False:
                True if function should omit "game/" from detected path to make
                it relative to "game/" folder.

        OUT:
            str:
                Relative (to DDLC directory) path to the .rpy script file that
                is currently being executed, or fallback value (or None if not
                provided) if this function is unable to find appropriate path.

        RAISES:
            ValueError:
                If fallback does not start with "game/" and relative is set to
                False.

        NOTE:
            For consistency between platforms (and further usage in Ren'Py
            functions and related things) paths returned always have "/" as
            folder separator, even on Windows.

            Also note that even though it is possible for script file to be
            located not in "game/" folder for somewhere else, this function
            assumes it is located in "game/" and uses this assumption in its
            path correction logic.

            Proper functionality of this function cannot be guaranteed if called
            from eval() and alike dynamic code execution contexts.
        """

        if (
            fallback is not None and not fallback.startswith("game/") and
            not relative
        ):
            raise ValueError(
                "fallback path does not start with \"game/\" "
                "and relative is not True"
            )

        # Use renpy's developer function get_filename_line() to get current
        # script location. WARNING: THIS IS EXTREMELY UNSTABLE, THE FOLLOWING
        # CODE IS THE WORKAROUND THAT MAKES IT SOMEWHAT RELIABLE! Also replace
        # Windows \ (backslash) folder separators with / (slash) character
        # for consistency.
        path = renpy.get_filename_line()[0].replace("\\", "/")
        if os.path.isabs(path):
            # Returned path may be absolute, relativize it.
            path = os.path.relpath(path, renpy.config.renpy_base)

        # Split current file path into components. Our strategy here:
        # 1. Get path components.
        # 2. Check if path starts with game/ folder.
        # 3. While it does not, drop first i+1 (initially i=0) parts from it
        #    and prepend it with game/.
        # 4a. If new path from 3. exists, we most likely have got the right path.
        # 4b. If new path from 3. doesn't exist, increment i by 1 and drop more
        #     path components from the original path and repeat 3.
        parts = path.split("/")  # (1.)
        if parts[0] != "game":  # (2.)
            for n in range(1, len(parts)):  # (3.)
                parts_proc = parts[n:]
                parts_proc.insert(0, "game")

                rel_path = "/".join(parts_proc)
                if os.path.exists(os.path.join(renpy.config.renpy_base, rel_path)):
                    result = rel_path.replace("\\", "/")  # (4a.)
                    if relative:
                        # Omit "game/" prefix (5 chars.)
                        return result[5:]
                    return result

                # else (4b.)

            if fallback is not None and relative:
                return fallback[5:]  # Omit game/ prefix, its presence is checked above.
            return fallback.replace("\\", "/") if fallback is not None else None

        else:
            if relative:
                # Simply remove leading "game" item frm path parts.
                parts.pop(0)
            return "/".join(parts)

    def _get_conf_dir():
        _file = _get_script_file(fallback="game/Submods/Discord Presence Submod")
        return os.path.join("/".join(_file.split("/")[:-1]), "config")

    config_dir = _get_conf_dir()


    def _parse_bool(s):
        if s.lower() in ("true", "yes", "y"):
            return True
        return False

    def _get_conf_value(parser, section, value, deserializer=str, default=None):
        try:
            return deserializer(parser.get(section, value, raw=True))
        except (configparser.NoOptionError, configparser.NoSectionError) as e:
            return default

    def _provider(provide):
        return type("Provider", (object, ), dict(
            get=lambda self: provide()
        ))()


    _timestamp_type = dict()

    def _dt_to_ts(dt):
        return int(time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0)

    def _ts_none():
        return None
    _timestamp_type["None"] = _provider(_ts_none)

    def _ts_session_start():
        return _dt_to_ts(persistent.sessions["current_session_start"])
    _timestamp_type["SessionStart"] = _provider(_ts_session_start)

    def _parse_ts_provider(s):
        return _timestamp_type.get(s)


    def _subst_str_provider(s):
        def provide():
            return renpy.substitute(s, _ext_vars)
        return _provider(provide)


    class Config(object):
        def __init__(self, parser):
            condition = _get_conf_value(parser, "Presence", "Condition")
            compile(condition, "<string>", "eval")
            self.condition = condition
            self.priority = _get_conf_value(parser, "Presence", "Priority", int)

            self.app_id = _get_conf_value(parser, "Client", "ApplicationID", int)
            self.retry_on_fail = _get_conf_value(parser, "Client", "RetryOnFail", _parse_bool)

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


    _configs = list()

    def _load_configs():
        for _dir, _, files in os.walk(config_dir):
            for _file in files:
                _configs.append(Config.load_file(os.path.join(_dir, _file)))


    def get_active_config():
        active = list()

        for conf in _configs:
            if bool(eval(conf.condition, _ext_vars, store.__dict__)):
                active.append(conf)

        if len(active) == 0:
            return None

        active.sort(key=lambda it: it.priority, reverse=True)
        return active[0]