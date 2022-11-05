# 🔌 Overriding default config

Discord Presence Submod ships with a sensible and constantly growing default
config set, which can be inconvenient to work with directly if you want to
customize it to suit your own tastes; however, one can create their own config
file with higher priority in order to override a default config.

For instance, if you want to override config events/anni-year.conf, which has
priority of -100, create your own config with the same condition (per your
needs) and priority of -99.

## Default configs and priorities

Below you can see a table with default config files and their priorities for
your convenience in finding a desired config and its priority without a need to
dig up every single file.

### Config shown when console is open

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -20      | misc/console.conf                                                       |

### Configs shown on game

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -20      | games/hangman.conf                                                      |
| -20      | games/chess.conf                                                        |
| -20      | games/nou.conf                                                          |
| -20      | games/piano.conf                                                        |
| -20      | games/pong.conf                                                         |

### Configs shown on topic

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -20      | topics/exp-previewer.conf                                               |
| -20      | topics/say-something-say.conf                                           |
| -20      | topics/say-something-pose.conf                                          |
| -20      | topics/floating-islands.conf                                            |

### Configs shown on anniversary/milestone day

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -90      | events/anni-year-day.conf                                               |
| -90      | events/anni-milestone-day.conf                                          |

### Configs shown a week before anniversary/milestone

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -100     | events/anni-year.conf                                                   |
| -100     | events/anni-milestone.conf                                              |

### Configs shown on player's or Monika's birthday

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -190     | events/player-bday-day.conf                                             |
| -190     | events/moni-bday-day.conf                                               |

### Configs shown a week before player's or Monika's birthday

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -200     | events/player-bday.conf                                                 |
| -200     | events/moni-bday.conf                                                   |

### Configs shown during be right back idle

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -600     | be-right-backs/my-otter-self-brbs/stretching.conf                       |
| -600     | be-right-backs/my-otter-self-brbs/stimulation.conf                      |
| -600     | be-right-backs/my-otter-self-brbs/social.conf                           |
| -600     | be-right-backs/my-otter-self-brbs/plants.conf                           |
| -600     | be-right-backs/my-otter-self-brbs/nails.conf                            |
| -600     | be-right-backs/my-otter-self-brbs/liedown.conf                          |
| -600     | be-right-backs/my-otter-self-brbs/journal.conf                          |
| -600     | be-right-backs/my-otter-self-brbs/food.conf                             |
| -600     | be-right-backs/my-otter-self-brbs/date.conf                             |
| -600     | be-right-backs/my-otter-self-brbs/call.conf                             |
| -600     | be-right-backs/misc/radio.conf                                          |
| -600     | be-right-backs/misc/podcast.conf                                        |
| -600     | be-right-backs/misc/panic.conf                                          |
| -600     | be-right-backs/misc/overstimulated.conf                                 |
| -600     | be-right-backs/misc/listening2.conf                                     |
| -600     | be-right-backs/misc/listening.conf                                      |
| -600     | be-right-backs/misc/jamming.conf                                        |
| -600     | be-right-backs/misc/drama.conf                                          |
| -600     | be-right-backs/mas/writing.conf                                         |
| -600     | be-right-backs/mas/workout.conf                                         |
| -600     | be-right-backs/mas/working.conf                                         |
| -600     | be-right-backs/mas/showering.conf                                       |
| -600     | be-right-backs/mas/reading.conf                                         |
| -600     | be-right-backs/mas/napping.conf                                         |
| -600     | be-right-backs/mas/homework.conf                                        |
| -600     | be-right-backs/mas/generic.conf                                         |
| -600     | be-right-backs/mas/gaming.conf                                          |
| -600     | be-right-backs/mas/coding.conf                                          |
| -600     | be-right-backs/mas/break.conf                                           |
| -600     | be-right-backs/genetechnician-reading-submod/watching_movie_videos.conf |
| -600     | be-right-backs/genetechnician-reading-submod/watching_game.conf         |
| -600     | be-right-backs/genetechnician-reading-submod/watching_drawing.conf      |
| -600     | be-right-backs/genetechnician-reading-submod/watching_code.conf         |
| -600     | be-right-backs/genetechnician-reading-submod/reading_romance.conf       |
| -600     | be-right-backs/genetechnician-reading-submod/reading_misc.conf          |
| -600     | be-right-backs/genetechnician-reading-submod/reading_manga.conf         |
| -600     | be-right-backs/genetechnician-reading-submod/reading_horror.conf        |
| -600     | be-right-backs/genetechnician-reading-submod/reading_dystopian.conf     |

### Config shown on a special date

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -790     | events/all-day.conf                                                     |

### Config shown a week before special date

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -800     | events/all.conf                                                         |

### Configs shown during night or morning

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -950     | time-of-day/night.conf                                                  |
| -950     | time-of-day/morning.conf                                                |

### Configs shown during specific weather

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -995     | weather/thunder.conf                                                    |
| -995     | weather/snow.conf                                                       |
| -995     | weather/rain.conf                                                       |

### Default/fallback config

| Priority | Config                                                                  |
|----------|-------------------------------------------------------------------------|
| -1000    | default.conf                                                            |