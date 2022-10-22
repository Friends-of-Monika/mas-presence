# 🔧 Customizing Discord Presence Submod

While Discord Presence Submod configuration system is made to be simple and easy
to understand, one might need a helping hand to figure what is what and how
things can be done with it, and this document is exactly what you need.

If you're looking for a way to override *default* config files, see
[DEFAULTS.md](DEFAULTS.md) page for details.

## Examples

If you feel like learning by example, you might as well look into `config/`
folder which contains all maintained presence config files that are well
commented and documented for your convenience and understanding as well as
[EXAMPLES.md](EXAMPLES.md) page. If you want to learn some theory though, here
it is, right below.

## Basic principles

### Presence Config files

Discord Rich Presence is built based on *Presence Configs*, files located in
`config/` folder that describe the conditions under which this activity (info
displayed on Rich Presence block on Discord profile) will be used and activity
properties.

The file name doesn't mean anything to submod and only helps you distinguish
presence configs from each other; however, config files must have one of the
following extensions: `.cfg`, `.ini` or `.conf`, files with any other extensions
will be ignored.

### Conditions and priorities

To reflect changes in game and let you display different activities based on
some input data, presence configs have *conditions* and *priorities* that
combined determined which presence config will be chosen on next loop.

*Condition* is a Python expression that evaluates in global MAS scope (this
means you can access any variables and Ren'Py stores in it), and if it results
in `True` (or any other value that, when casted to boolean, will be `True`) will
enable this presence config to be counted in for the next presence update.

Of course, there will be cases when *several* configs have matching conditions,
and that's when *Priority* comes in handy. Every presence config has priority
parameter, and after config conditions have been evaluated and eligible configs
were lined up, they will be sorted by their priority (higher values first, e.g.
of two eligible configs with values 50 and 100 one with value of 100 will be
used) and one with the highest priority will be chosen. However, there's no
guarantee that configs with equal priorities will be chosen in certain order
or that they will have equal probability to be chosen; in this case the
behaviour is undefined and any config may be chosen.

### Variable interpolation

In activity text lines and assets image captions, it is possible to
*interpolate* variables using Ren'Py standard syntax `[variable_name]`; in
addition to that, Python syntax is supported to some extent, and it is possible
to invoke functions in order to get some value: `[function(arguments...)]`.

Interpolation is performed in global scope, meaning all MAS (and submods)
variables can be accessed (like `[m_name]`, `[player]` and so on.)

## Advanced concepts

### Extensions

Extensions aren't specifically a Discord Presence Submod-powered feature,
however one could create a `.rpy` file and export custom variables, operate on
data, manage presence directly, etc.

Discord Presence Submod ships with few extensions maintained by project creators
and maintainers:

* `fom-custom-vars.rpy` provides Custom Variables framework for registering and
  updating custom variables that can be used in expressions and interpolations.
* `fom-events.rpy` provides custom variables related to upcoming calendar
  events.
* `fom-functions.rpy` provides custom functions that can be found useful in
  interpolations.
* `fom-locations.rpy` provides custom variable for displaying currently active
  background.

### Inheritance

As amount of configs made for Discord Presence Submod grows, so grows the
redundancy of values shared by several config. To accord for this, a config ID
and inheritance mechanism was introduced in 0.3.0, which allows setting config
ID and refer to it in another configs to *copy all missing values* over to
another config. And in case inherited config inherits from another config...
Yes, inheritance is processed *recursively.* :)

A real example would be default config which has grown quite big and
redundantly filled with default `State`, `[Assets]` and other things that one
would have to change *in every file* if they wanted to override something. To
improve this situation, we used `ID = default` and `Inherit = Default` in every
config and removed redundant copies of application ID, assets and text.

#### Parent config (copy FROM) example

```ini
[Presence]
ID = Default
```

#### Child config (copy TO) example

```ini
[Presence]
Inherit = Default
```

Inheritance is processed recursively, which means you can have one config (A)
inherit values from another (B), then one more config (C) would inherit values
from A and have values both from A and from B.

Only omitted values are replaced, in case some value is present in the child
config it will never be replaced.

### Overriding

Continuing to counter issues with default config customization, in patch 0.3.1
two more important parameters have been introduced with one of them being
`Override =`.

With `Override`, you can replace existing config by its ID or path (relative to
config directory, see example below) *entirely*, combined with `Inherit` (see
above) you could could use it to alter just a part of existing config without
a need to copy it entirely.

#### Existing config

```ini
[Presence]
ID = MyAwesomeConfig

[Activity]
State = Having fun at [loc_prompt]
```

#### Overriding config

```ini
[Presence]
Override = MyAwesomeConfig

[Activity]
State = Spending time together at [loc_prompt]
```

Sometimes however, if an existing config has no ID assigned and you don't want
to edit it, you can use a path (relative to config directory) instead:

```ini
[Presence]
# Full path would be game/Submods/Discord Presence Submod/config/default/...
# but you only need part AFTER config/, without a leading slash (/)
Override = default/configs/default.conf
```

Taking possible override conflicts into account, if there are is more than one
override existing for a certain config, one with higher priority prevails.

### Disabling

Another parameter introduced in 0.3.1 is `Disable =`, which if set to `True`
will disable the config and prevent it from being chosen. This however does not
affect inheriting and overriding and you can still use it as a base for other
configs or override some other config and disable it.

For example, if there is a default config you want to disable, you'd create
another config and use `Override` like this:

```ini
[Presence]
Override = default/configs/some-config-to-disable.conf
Disable = True
```

This config will replace a config you specified in `Override` and disable it,
making it never be chosen.