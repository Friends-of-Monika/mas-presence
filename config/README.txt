                                         ___  _              __
                                       .' ..](_)            / /
               .---.   .--.   _ .--.  _| |_  __   .--./)   / /
              / /'`\]/ .'`\ \[ `.-. |'-| |-'[  | / /'`\;  / /
              | \__. | \__. | | | | |  | |   | | \ \._// / /
              '.___.' '.__.' [___||__][___] [___].',__` /_/
                                                ( ( __))


This folder contains configuration files for the Discord Presence Submod that
define what presence is chosen for display and what is shown on it.

To keep default presence configs updated with new submod releases, they
were put into default/ folder which you should not touch, and rather put your
own configs outside this folder and set their priority to values greater than
specified in default configs so they will override them. For instance, if you
want to override config events/anni-year.conf, which has priority of -100,
create your own config with the same condition (per your needs) and priority
of -99.

The config system is made to be simple but infinitely extensible, however if
you're having trouble figuring out how to configure things, check out this page:
https://github.com/Friends-of-Monika/mas-presence/blob/master/doc/CUSTOMIZING.md

Additionally, here is the list of default configs and priorities for convenience
of custom overrides of default configs:

  Priority  Config
  --------  ------
  -90       events/anni-year-day.conf
  -90       events/anni-milestone-day.conf
  -100      events/anni-year.conf
  -100      events/anni-milestone.conf
  -190      events/player-bday-day.conf
  -190      events/moni-bday-day.conf
  -200      events/player-bday.conf
  -200      events/moni-bday.conf
  -600      be-right-backs/my-otter-self-brbs/stretching.conf
  -600      be-right-backs/my-otter-self-brbs/stimulation.conf
  -600      be-right-backs/my-otter-self-brbs/social.conf
  -600      be-right-backs/my-otter-self-brbs/plants.conf
  -600      be-right-backs/my-otter-self-brbs/nails.conf
  -600      be-right-backs/my-otter-self-brbs/liedown.conf
  -600      be-right-backs/my-otter-self-brbs/journal.conf
  -600      be-right-backs/my-otter-self-brbs/food.conf
  -600      be-right-backs/my-otter-self-brbs/date.conf
  -600      be-right-backs/my-otter-self-brbs/call.conf
  -600      be-right-backs/misc/radio.conf
  -600      be-right-backs/misc/podcast.conf
  -600      be-right-backs/misc/panic.conf
  -600      be-right-backs/misc/overstimulated.conf
  -600      be-right-backs/misc/listening2.conf
  -600      be-right-backs/misc/listening.conf
  -600      be-right-backs/misc/jamming.conf
  -600      be-right-backs/misc/drama.conf
  -600      be-right-backs/mas/writing.conf
  -600      be-right-backs/mas/workout.conf
  -600      be-right-backs/mas/working.conf
  -600      be-right-backs/mas/showering.conf
  -600      be-right-backs/mas/reading.conf
  -600      be-right-backs/mas/napping.conf
  -600      be-right-backs/mas/homework.conf
  -600      be-right-backs/mas/generic.conf
  -600      be-right-backs/mas/gaming.conf
  -600      be-right-backs/mas/coding.conf
  -600      be-right-backs/mas/break.conf
  -600      be-right-backs/genetechnician-reading-submod/watching_movie_videos.conf
  -600      be-right-backs/genetechnician-reading-submod/watching_game.conf
  -600      be-right-backs/genetechnician-reading-submod/watching_drawing.conf
  -600      be-right-backs/genetechnician-reading-submod/watching_code.conf
  -600      be-right-backs/genetechnician-reading-submod/reading_romance.conf
  -600      be-right-backs/genetechnician-reading-submod/reading_misc.conf
  -600      be-right-backs/genetechnician-reading-submod/reading_manga.conf
  -600      be-right-backs/genetechnician-reading-submod/reading_horror.conf
  -600      be-right-backs/genetechnician-reading-submod/reading_dystopian.conf
  -790      events/all-day.conf
  -800      events/all.conf
  -950      time-of-day/night.conf
  -950      time-of-day/morning.conf
  -995      weather/thunder.conf
  -995      weather/snow.conf
  -995      weather/rain.conf
  -1000     default.conf