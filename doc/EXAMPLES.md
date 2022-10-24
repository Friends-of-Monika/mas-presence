# 📚 Configuration examples

On this page you can see various examples of presence configs. For brevity
(texts and assets are self explanatory) only `[Presence]` part is shown unless
there is something peculiar to look at in text/assets configuration in this very
case.

## Static configuration

If you don't want your presence dynamic (e.g. changing depending on context),
you can stick to static configuration:

```ini
[Presence]
# Having this set to 'True' will ensure config will always be active.
Condition = True
# Highest priority will mean it will always be chosen as presence config.
Priority = 1000
# 'False' will disable evaluation of variables in texts.
Dynamic = False
```

## Fallback configuration

In case there are no active configurations available, the submod will clear the
activity display (but will maintain the connection to quickly render it again
when available.)

To ensure at least something is displayed, it is useful to have a *fallback*
config:

```ini
[Presence]
# Since this is set to 'True', this config will always be active.
Condition = True
# With the lowest priority, this config will only be chosen when no other
# configs are available.
Priority = -1000
Dynamic = True
```

## Time of day based configuration

Using `mas_globals.time_of_day_4state` variable, you can create a config that
will only become active in your desired time of day. Available values (put
them in `""` after `==`):
* `morning`
* `afternoon`
* `evening`
* `night`

```ini
[Presence]
Condition = mas_globals.time_of_day_4state == "morning"
Priority = -950
Dynamic = True
```

## Weather based configuration

Using `mas_current_weather` one can create a config that will be active when
there is a certain type of weather in Monika's world:

Here's list of currently available values (not that unlike in other examples,
these are not strings, and they are deliberately written without quotes):
* `mas_weather_def`
* `mas_weather_rain`
* `mas_weather_snow`
* `mas_weather_thunder`
* `mas_weaher_overcast`

```ini
[Presence]
Condition = mas_current_weather == mas_weather_rain
Priority = -995
Dynamic = True
```

## Topic based configuration

Using custom variable `event_label`, you can create a config that will be chosen
as soon as player enters a certain topic. Here's how:

```ini
[Presence]
Condition = event_label == "monika_hemispheres"
Priority = -20
Dynamic = True
```

There isn't a list of available values for this, but you can look into [Monika
After Story](https://github.com/Monika-After-Story/MonikaModDev/blob/master/Monika%20After%20Story/game/script-topics.rpy#L868)
source code and get event labels from there, as well as custom labels from
submods.