# This file is part of Discord Presence Submod (see link below):
# https://github.com/friends-of-monika/mas-presence

default persistent._fom_presence_enabled = True

init 90 python in _fom_presence_config:
    import store

    from store import persistent
    from store import _fom_presence as mod
    from store import _fom_presence_util as util
    from store import _fom_presence_discord as discord
    from store import _fom_presence_status as status
    from store import _fom_presence_logging as logging

    import sys
    import os
    import time
    import traceback

    if sys.version_info.major == 2:
        import ConfigParser as configparser
        import io
    else:
        import configparser


    # Problems shown in settings pane (see status.rpy)

    _STATUS_CONFIG_PREFIX = "config:"

    def _report_config_problem(kind, rel_file, ui_message, log_message, level=status.ERROR):
        status.set(
            "{0}{1}:{2}".format(_STATUS_CONFIG_PREFIX, kind, rel_file),
            ui_message, log_message, level
        )


    # Timestamps and related functions and variables

    def _datetime_to_int(dt):
        """
        Converts datetime instance to Unix milliseconds timestamp.

        IN:
            dt -> datetime.datetime:
                Datetime to convert.

        OUT:
            int:
        """

        return int(time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0)


    timestamps_db = dict()
    timestamps_db["none"] = util.SUPPLY_NONE

    def _parse_ts_supplier(s):
        """
        Parses provided string to retrieve a timestamp supplier from database.

        IN:
            s -> str:
                Timestamp supplier name, case insensitive.

        OUT:
            Supplier:
                Supplier that provides a timestamp.

            None:
                If none found by the specified name.
        """

        return timestamps_db.get(s.lower())

    def _timestamp_session_start():
        """
        Supplier that provides session begin timestamp.

        OUT:
            int:
                Unix timestamp of session begin.
        """
        return _datetime_to_int(persistent.sessions["current_session_start"])

    timestamps_db["sessionstart"] = util.Supplier(_timestamp_session_start)

    def _timestamp_brb_start():
        """
        Supplier that provides timestamp of when be right back has started.

        OUT:
            int:
                Unix timestamp of be right back beginning.
        """

        if not store.mas_globals.in_idle_mode:
            return None
        brb_ev = store.mas_getEV(store.mas_submod_utils.last_label)
        return _datetime_to_int(brb_ev.last_seen)
    timestamps_db["berightbackstart"] = util.Supplier(_timestamp_brb_start)

    def _timestamp_last_update():
        """
        Supplier that provides timestamp of last meaningful presence update.

        OUT:
            int:
                Unix timestamp of last presence update.
        """

        dt = mod.presence.last_meaningful_update
        if dt is None:
            return None
        return _datetime_to_int(dt)
    timestamps_db["lastpresenceupdate"] = util.Supplier(_timestamp_last_update)


    # ConfigParser wrapper and related functions and classes

    def _parse_bool(s):
        """
        Parses a string and returns a boolean value for its content.
        Values "true", "yes", "y" (case-insensitive) will be considered True,
        anything else will be False.

        IN:
            s -> str:
                String to parse boolean from.

        OUT:
            True:
                For strings "true", "yes", "y" (case-insensitive.)

            False:
                For any other strings.
        """

        if s.lower() in ("true", "yes", "y"):
            return True
        return False

    if sys.version_info.major == 2:
        def _open_with_encoding(path, mode, encoding="utf-8"):
            """
            Opens file with specified encoding.

            IN:
                path -> str:
                    Path to file to open.

                mode -> str:
                    Mode of file to open, see built-in function open(...)

                encoding -> str, default "utf-8":
                    Encoding to use when reading/writing to file.

            OUT:
                File-like object:
                    File opened in the provided mode with provided encoding.
            """

            return io.open(path, mode, encoding="utf-8")
    else:
        def _open_with_encoding(path, mode, encoding="utf-8"):
            """
            Opens file with specified encoding.

            IN:
                path -> str:
                    Path to file to open.

                mode -> str:
                    Mode of file to open, see built-in function open(...)

                encoding -> str, default "utf-8":
                    Encoding to use when reading/writing to file.

            OUT:
                File-like object:
                    File opened in the provided mode with provided encoding.
            """

            return open(path, mode, encoding="utf-8")

    class _ParserWrapper(object):
        """
        ParserWrapper is a wrapper for ConfigParser that provides get_value(...)
        method for reading strings and deserializing them to proper data types.
        """

        def __init__(self, parser):
            """
            Creates a new instance of ParserWrapper with the provided
            ConfigParser instance to wrap.

            IN:
                parser -> configparser.ConfigParser:
                    ConfigParser instance to wrap.
            """

            self._parser = parser

        def get_value(self, section, value, deserializer=str, default=None):
            """
            Gets value from underlying ConfigParser instance and applies
            deserialization logic on it.

            IN:
                section -> str:
                    Section to load value from.

                value -> str:
                    Key of the value to retrieve.

                deserializer -> function, default str:
                    Deserializer function to apply to retrieved string.

                default -> any, default None:
                    Default value to return if there is no such section/value.
            """

            try:
                return deserializer(self._parser.get(section, value, raw=True))
            except (configparser.NoOptionError, configparser.NoSectionError) as e:
                return default


    # Config object and related functions and variables

    class Config(object):
        """
        Config provides uniform way to access data stored in .conf/.ini/.cfg
        files that is loaded using ParserWrapper and deserializers.
        """

        def __init__(self, parser):
            """
            Creates a new instance of Config with the provided ParserWrapper
            to load values with.

            IN:
                parser -> ParserWrapper:
                    ParserWrapper that will load values from ConfigParser.
            """

            condition = parser.get_value("Presence", "Condition")
            if condition is not None:
                condition = condition.strip()
                if len(condition) > 0:
                    compile(condition, "<string>", "eval")
                else:
                    condition = None
            self.condition = condition

            self.priority = parser.get_value("Presence", "Priority", int, 0)
            self.dynamic = parser.get_value("Presence", "Dynamic", _parse_bool, True)
            self.id = parser.get_value("Presence", "ID", str, None)
            self.inherit_id = parser.get_value("Presence", "Inherit", str, None)
            self.override_id = parser.get_value("Presence", "Override", str, None)
            self.disable = parser.get_value("Presence", "Disable", _parse_bool, False)

            self.app_id = parser.get_value("Client", "ApplicationID", int)

            self.details = parser.get_value("Activity", "Details", util.supply_subsitute, util.SUPPLY_NONE)
            self.state = parser.get_value("Activity", "State", util.supply_subsitute, util.SUPPLY_NONE)

            self.large_image = parser.get_value("Assets", "LargeImage")
            self.large_text = parser.get_value("Assets", "LargeText", util.supply_subsitute, util.SUPPLY_NONE)
            self.small_image = parser.get_value("Assets", "SmallImage")
            self.small_text = parser.get_value("Assets", "SmallText", util.supply_subsitute, util.SUPPLY_NONE)

            self.start_ts = parser.get_value("Timestamps", "Start", _parse_ts_supplier, util.SUPPLY_NONE)
            self.stop_ts = parser.get_value("Timestamps", "End", _parse_ts_supplier, util.SUPPLY_NONE)

            self._activity = None
            self._file = None

        @staticmethod
        def from_file(path):
            """
            Loads Config from path.

            IN:
                path -> str:
                    Path to config file.

            OUT:
                Config:
                    Config loaded from file.
            """

            c = configparser.ConfigParser()
            with _open_with_encoding(path, "r", encoding="utf-8") as f:
                c.readfp(f, path.replace("\\", "/"))

            config = Config(_ParserWrapper(c))
            config._file = path
            return config

        @property
        def file(self):
            """
            Returns path to file this config was loaded from.

            OUT:
                str:
                    Path to config file.
            """

            return self._file

        def copy_from(self, config):
            """
            Copies values from another config (only omitted, None or
            util.SUPPLY_NONE values) over to this config.

            IN:
                config -> Config:
                    Config to copy values from.
            """

            if self.app_id is None:
                self.app_id = config.app_id
            if self.details is util.SUPPLY_NONE:
                self.details = config.details
            if self.state is util.SUPPLY_NONE:
                self.state = config.state
            if self.large_image is None:
                self.large_image = config.large_image
            if self.large_text is util.SUPPLY_NONE:
                self.large_text = config.large_text
            if self.small_image is None:
                self.small_image = config.small_image
            if self.small_text is util.SUPPLY_NONE:
                self.small_text = config.small_text
            if self.start_ts is util.SUPPLY_NONE:
                self.start_ts = config.start_ts
            if self.stop_ts is util.SUPPLY_NONE:
                self.stop_ts = config.stop_ts

        def to_activity(self):
            """
            Creates Activity instance from the values stored in Config.
            If dynamic property is set to False this is only evaluated once,
            stored in _activity and then retrieved from it on next call, not
            re-evaluating suppliers and not building fresh Activity.

            OUT:
                Activity:
                    Activity based on properties this Config instance has.
            """

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
    _config_id_map = dict()
    _config_path_map = dict()

    def reload_configs():
        """
        Clears global _configs variable and populates it with new valid configs.
        If reloading fails unexpectedly, previously loaded configs are kept.

        NOTE:
            Problems are reported to status module; problems reported on
            previous loads are cleared.
        """

        status.clear_prefix(_STATUS_CONFIG_PREFIX)

        try:
            configs, ids, paths = _load_configs()
        except Exception:
            logging.DEFAULT.error("Could not reload presence configs:\n{0}".format(traceback.format_exc()))
            status.set(
                _STATUS_CONFIG_PREFIX + "reload",
                "Could not reload configs, see log/submod_log.log."
            )
            return

        # Re-populate config list, sorted on reload to save precious time on
        # every loop (and by path too, so that ties are resolved the same way
        # every time.)
        del _configs[:]
        _configs.extend(sorted(configs.items(), key=lambda it: _load_order(it[1])))

        # Re-populate ID and path maps.
        _config_id_map.clear()
        _config_id_map.update(ids)
        _config_path_map.clear()
        _config_path_map.update(paths)

    def _normalize_ref(ref):
        """
        Normalizes config reference (ID or path relative to config directory)
        so that paths always use "/" as folder separator.

        IN:
            ref -> str:
                Reference to normalize.

        OUT:
            str:
                Normalized reference.
        """

        ref = ref.strip().replace("\\", "/")
        while ref.startswith("./"):
            ref = ref[2:]
        return ref.lstrip("/")

    def _lookup(ref, ids, paths):
        """
        Looks up config by reference, trying it as an ID first and as a path
        (relative to config directory) second.

        IN:
            ref -> str or None:
                Config ID or path.

            ids -> dict:
                Map of config ID to Config instance.

            paths -> dict:
                Map of config path to Config instance.

        OUT:
            Config:
                If config was found.

            None:
                If no config matches reference.
        """

        if ref is None:
            return None
        ref = _normalize_ref(ref)
        config = ids.get(ref)
        if config is None:
            config = paths.get(ref)
        return config

    def _load_order(config):
        """
        Sort key that orders configs by priority (highest first) and then by
        path, so that order is the same on every load and every platform.
        """

        return (-config.priority, config.file)

    def _load_configs():
        """
        Loads configs from config directory and applies overrides and
        inheritance.

        OUT:
            tuple of (configs, ids, paths):
                configs -> dict:
                    Map of config path (relative to config directory, with
                    "/" separators) to Config instance.

                ids -> dict:
                    Map of config ID to Config instance.

                paths -> dict:
                    Map of config path to Config instance.
        """

        configs = dict()

        for _dir, _, files in os.walk(_config_dir):
            for _file in files:
                if not (
                    _file.endswith(".ini") or
                    _file.endswith(".cfg") or
                    _file.endswith(".conf")
                ):
                    continue

                _file = os.path.join(_dir, _file)
                rel_file = os.path.relpath(_file, _config_dir).replace(os.sep, "/")

                try:
                    config = Config.from_file(_file)
                    if config.condition is not None:
                        eval(config.condition, dict(), store.__dict__)
                    config._file = rel_file
                except Exception as e:
                    _report_config_problem(
                        "loading", rel_file,
                        "Could not load config {0}, see log/submod_log.log.".format(rel_file),
                        "Could not load presence config from file {0}: {1}.".format(rel_file, e)
                    )
                    continue

                configs[rel_file] = config

        # Build path and ID maps. When several configs share an ID, the one
        # with the highest priority (then the first by path) gets it.
        paths = dict(configs)
        ids = dict()
        for config in sorted(configs.values(), key=_load_order):
            if config.id is None:
                continue

            owner = ids.get(config.id)
            if owner is None:
                ids[config.id] = config
                continue

            _report_config_problem(
                "clash", config.file,
                "Config {0} has ID {1} already used by config {2}.".format(config.file, config.id, owner.file),
                "Presence config {0} has ID {1} already used by config {2} (which takes precedence.)".format(config.file, config.id, owner.file),
                status.WARNING
            )

        def remove(config):
            # Configs may be removed more than once (e.g. losing override that
            # also fails inheritance) and may share ID with another config, so
            # only drop map entries that still point to this config.
            configs.pop(config.file, None)
            if paths.get(config.file) is config:
                del paths[config.file]
            if config.id is not None and ids.get(config.id) is config:
                del ids[config.id]

        # Build override map (config to override to list of configs willing to
        # override it); references are resolved first so that the same config
        # referenced by ID and by path is treated as one.
        override_map = dict()
        for config in sorted(configs.values(), key=_load_order):
            if config.override_id is None:
                continue

            target = _lookup(config.override_id, ids, paths)
            if target is None or target is config:
                _report_config_problem(
                    "override", config.file,
                    "Config {0} overrides unknown config ID {1}.".format(config.file, config.override_id),
                    "Presence config {0} overrides nonexistent config ID: {1}.".format(config.file, config.override_id)
                )
                continue

            override_map.setdefault(target, []).append(config)

        # Keep configs replaced by overrides reachable for overrides that also
        # inherit from the config they replace.
        replaced = dict()

        # Apply overrides. Overrides are already sorted by priority, so the
        # first one wins.
        for target in sorted(override_map, key=lambda it: it.file):
            overrides = override_map[target]
            for rem_conf in (overrides[1:] + [target]):
                remove(rem_conf)

            # Override takes place of the replaced config under both its ID
            # and path, so that both keep referring to it.
            override = overrides[0]
            if target.id is not None:
                override.id = target.id
                ids[target.id] = override
            paths[target.file] = override
            replaced[override] = target

        inherited = set()
        failed = set()

        def report_inheritance(config, ui_message, log_message):
            failed.add(config)
            _report_config_problem("inheritance", config.file, ui_message, log_message)

        def inherit(config, chain):
            if config in inherited:
                return True
            if config in failed:
                return False

            if config in chain:
                cycle = chain[chain.index(config):] + [config]
                cycle_str = " -> ".join(it.file for it in cycle)
                for member in cycle[:-1]:
                    report_inheritance(
                        member,
                        "Config {0} is part of inheritance cycle, see log/submod_log.log.".format(member.file),
                        "Presence config {0} is part of inheritance cycle: {1}.".format(member.file, cycle_str)
                    )
                return False

            if config.inherit_id is not None:
                parent = _lookup(config.inherit_id, ids, paths)
                if parent is config and config in replaced:
                    # Override inheriting from the config it replaces.
                    parent = replaced[config]

                if parent is None:
                    report_inheritance(
                        config,
                        "Config {0} inherits unknown config ID {1}.".format(config.file, config.inherit_id),
                        "Presence config {0} inherits nonexistent config ID: {1}.".format(config.file, config.inherit_id)
                    )
                    return False

                if not inherit(parent, chain + [config]):
                    if config not in failed:
                        report_inheritance(
                            config,
                            "Config {0} inherits from config {1} that could not be loaded.".format(config.file, parent.file),
                            "Presence config {0} inherits from config {1} that could not be loaded.".format(config.file, parent.file)
                        )
                    return False

                config.copy_from(parent)

            inherited.add(config)
            return True

        # Apply inheritance to remaining configs; parents (including removed
        # ones) are resolved recursively.
        for config in sorted(configs.values(), key=_load_order):
            inherit(config, [])

        for config in failed:
            remove(config)

        return configs, ids, paths

    def get_active_config():
        """
        Evaluates conditions in configs in global Ren'Py scope and returns
        config with the highest priority of all configs which conditions
        evaluated to True.

        NOTE:
            Condition evaluation problems are reported to status module and
            cleared once the condition evaluates successfully again.
        """

        for rel_file, conf in _configs:
            if not conf.disable and conf.condition is not None:
                try:
                    result = bool(eval(conf.condition, dict(), store.__dict__))
                except Exception as e:
                    _report_config_problem(
                        "condition", rel_file,
                        "Could not evaluate condition of config {0}, see log/submod_log.log.".format(rel_file),
                        "Could not evaluate condition of presence config {0}: {1}.".format(rel_file, e)
                    )
                    continue

                status.clear("{0}condition:{1}".format(_STATUS_CONFIG_PREFIX, rel_file))
                if result:
                    return conf

        return None

    def get_config(_id):
        """
        Fetches config by its ID (defined as ID= parameter in Presence section)
        or by its path relative to config directory.

        IN:
            _id -> str:
                ID or path of the config to fetch reference to.

        OUT:
            Config:
                If config with such ID or path exists and was successfully
                loaded.

            None:
                If config with such ID or path does not exist.
        """

        return _lookup(_id, _config_id_map, _config_path_map)
