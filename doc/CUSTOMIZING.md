# 🔧 Customizing Discord Presence Submod

While Discord Presence Submod configuration system is made to be simple and easy
to understand, one might need a helping hand to figure what is what and how
things can be done with it, and this document is exactly what you need.

If you're looking for a way to override *default* config files, see
[DEFAULTS.md](DEFAULTS.md) page for details.

## Examples

If you feel like learning by example, you might as well look into `config/`
folder which contains all maintained presence config files that are well
commented and documented for your convenience and understanding. If you want to
learn some theory though, here it is, right below.

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
