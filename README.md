<h1 align="center">🛰️ Discord Presence Submod</h1>
<h3 align="center">Show everyone who's the person you're spending your time with~</h3>

<p align="center">
  <a href="https://github.com/friends-of-monika/mas-presence/releases/latest">
    <img alt="Latest release" src="https://img.shields.io/github/v/release/friends-of-monika/mas-presence">
  </a>
  <a href="https://github.com/friends-of-monika/mas-presence/releases">
    <img alt="Release downloads" src="https://img.shields.io/github/downloads/friends-of-monika/mas-presence/total">
  </a>
  <a href="https://www.reddit.com/r/MASFandom/comments/y4mvl4/when_discord_meets_mas_discord_presence_submod_is">
    <img alt="Reddit badge" src="https://img.shields.io/badge/dynamic/json?label=%F0%9D%97%8B%2Fmasfandom%20post&query=%24[0].data.children[0].data.score&suffix=%20upvotes&url=https%3A%2F%2Fwww.reddit.com%2Fr%2FMASFandom%2Fcomments%2Fy4mvl4%2Fwhen_discord_meets_mas_discord_presence_submod_is.json&logo=reddit&style=social">
  </a>
  <a href="https://github.com/friends-of-monika/mas-presence/blob/main/LICENSE.txt">
    <img alt="MIT license badge" src="https://img.shields.io/badge/License-MIT-lightgrey.svg">
  </a>
  <a href="https://dcache.me/discord">
    <img alt="Discord server" src="https://discordapp.com/api/guilds/1029849988953546802/widget.png?style=shield">
  </a>
  <a href="https://ko-fi.com/Y8Y15BC52">
    <img alt="Ko-fi badge" src="https://ko-fi.com/img/githubbutton_sm.svg" height="20">
  </a>
</p>

<p align="center">
  <a href="https://github.com/friends-of-monika/mas-presence">
    <img alt="English version badge" src="https://img.shields.io/badge/🇬🇧_English-gray.svg">
  </a>
  <a href="https://github.com/MAS-Submod-MoyuTeam/mas-presence">
    <img alt="English version badge" src="https://img.shields.io/badge/🇨🇳_Chinese-gray.svg">
  </a>
</p>


## 🌟 Features

* Simple and minimalistic yet extremely extensible configuration
  * Create unlimited amount of presence configurations and switch between them
    using conditional expressions
  * Interpolate any accessible variables in text using familiar Ren'Py syntax
  * Several additional variables you can use in text and conditional expressions
* Configuration that works out of the box &mdash; just install it and
  see it work right away!
  * Ships with a ton of premade presence configs made for lots of possible
    special cases one could want to reflect on their Rich Presence
    * Calendar events detection and countdown
    * Dedicated presence config for anniversary dates
    * Time of day-based presences
    * Monika and her player's birthday special presence layouts
    * Support for Be Right Back in base game as well as custom be right backs
      from submods from my-otter-self, geneTechnician and other people!
    * Displays current game being played and also tells everyone whenever
      you admire floating islands scenery~
  * Contains custom variables extensions that can be used in text lines

### 📑 Comparison with other submods

| ⚙️ Submod             | 🏃 Startup time           | 🔧 Configuration                       | 🧬 Custom application ID |
|-----------------------|---------------------------|----------------------------------------|--------------------------|
| [Presence Submod][12] | ✔️ Starts right away      | 🔨 CONF-based,<br>free structured      | ✔️ Supported             |
| [MAS RPC][5]          | ⏰ Takes up to one minute | 🪡 JSON-based,<br>strict structured    | ✔️ Supported             |

| ⚙️ Submod             | 🕹️ Condition based displays                                                  | 🕑 Custom timestamps       | 🐍 Python and Ren'Py support  |
|-----------------------|------------------------------------------------------------------------------|----------------------------|-------------------------------|
| [Presence Submod][12] | 💃 Supports unlimited amount<br>of displays chosen based<br>on any condition | ⏰ Several premade options | 🎉 Python 2 & 3, Ren'Py 6 & 8 |
| [MAS RPC][5]          | 🚶 Supports just be<br>right backs and custom<br>locations                   | 🏃 Only startup time       | 💤 Python 2, Ren'Py 6         |


## ❓ Installing

1. Go to [the latest release page][6] and scroll to Assets section.
2. Download `discord-presence-submod-VERSION.zip` file.
3. Drag and drop `game/` folder from it into your DDLC folder.

   **NOTE:** make sure you don't drag it *into `game`*!
4. You're all set!~

## 📚 Customization

Discord Presence Submod is *infinitely* customizable with condition-driven
presence configs, interpolable text lines and extensions that can change the
entire way presence configs are chosen or processed.

Want to know how? Check out [customization guide][1]!

## 🏅 Special thanks

Discord Presence Submod authors, maintainers and contributors express their
gratitude to the following people:
* [Kventis][2] &mdash; Discord Rich Presence idea and [MAS RPC][5] submod.
* [PencilMario][7] &mdash; Chinese translation of repository and default config
  files.

Additionally, we thank these people for testing the submod before its public
release:
* [Otter][3] &mdash; early access preview.
* [MaximusDecimus][4] &mdash; early access preview.
* TheGuy &mdash; early access preview.

## 💬 Join our Discord

We're up to chat! Come join submod author's Discord server [here][8] or come to chat at Friends
of Monika Discord server [here][9].

[![Discord server invitation][10]][8]
[![Discord server invitation][11]][9]

[1]: doc/CUSTOMIZING.md
[2]: https://github.com/ImKventis
[3]: https://github.com/my-otter-self
[4]: https://github.com/AzhamProdLive
[5]: https://github.com/ImKventis/MAS_RPC
[6]: https://github.com/friends-of-monika/mas-presence/releases/latest
[7]: https://github.com/PencilMario
[8]: https://dcache.me/discord
[9]: https://mon.icu/discord
[10]: https://discordapp.com/api/guilds/1029849988953546802/widget.png?style=banner3
[11]: https://discordapp.com/api/guilds/970747033071804426/widget.png?style=banner3
[12]: https://github.com/friends-of-monika/mas-presence