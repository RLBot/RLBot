# RLBot v4 (Deprecated)

<p align="center">
  <img width="512" height="158" src="https://github.com/drssoccer55/RLBot/blob/master/images/RLBot.png">
</p>

[<img src="https://img.shields.io/pypi/v/rlbot.svg">](https://pypi.org/project/rlbot/)
[<img src="https://img.shields.io/maven-central/v/org.rlbot.commons/framework">](https://bintray.com/rlbotofficial/RLBotMaven/rlbot-framework)
[<img src="https://img.shields.io/nuget/v/RLBot.Framework">](https://www.nuget.org/packages/RLBot.Framework/)
[<img src="https://img.shields.io/crates/v/rlbot">](https://crates.io/crates/rlbot)
[<img src="https://img.shields.io/discord/348658686962696195.svg?colorB=7581dc&logo=discord&logoColor=white">](https://discord.gg/zbaAKPt)

RLBot is a framework for creating bots for Rocket League's offline modes, just for fun.
It provides values from the game like positions and velocities for cars and ball, and carries back button presses. RLBot was developed in collaboration is Psyonix, the developers of Rocket League, and it is therefore safe to use and cannot be used for cheating.


> [!IMPORTANT]
> RLBot v5 has been released!
> Learn more about RLBot v5 at https://wiki.rlbot.org/v5/framework/v5/.
> Find RLBot v5's core repository at https://github.com/RLBot/core.

> [!WARNING]
> RLBot v4 is deprecated and will not receive more updates.

## Want to play against bots?

People looking for bot opponents should check out the RLBotGUI available at https://rlbot.org/.

RLBotGUI features:
- A wide variety of community made bots to play against.
- A Story Mode with a series of escalating challenges.
- Developer tools such as appearance editor and state-setting sandbox.

Repository: https://github.com/RLBot/RLBotGUI

## Want to make a bot?

If you just want to make a bot, you probably want to start with one of these:

- Python - https://github.com/RLBot/RLBotPythonExample
- Java - https://github.com/RLBot/RLBotJavaExample
- C# (and other .NET languages) - https://github.com/RLBot/RLBotCSharpExample
- Scratch - https://github.com/RLBot/RLBotScratchInterface
- Rust - https://crates.io/crates/rlbot

Find all officially supported languages at https://rlbot.org/. You can also find a ton of resources on the [wiki](https://wiki.rlbot.org/v4/).

## Framework Development

This repository is currently incomplete to meet the legal needs of the Psyonix API. It is missing the source code behind RLBot.exe, and a few other files. If you want to make a code change that involves RLBot.exe (or the interface dll since it's closely related), you'll need some help from someone with access to the closed repo. Any commits to this repo will be pull to the closed-source repo.

### Requirements
Rocket League, Python 3.11+

### Quick Start

1. Run setup.bat (or equivalent if you're on Linux or Mac)
1. Open a terminal and execute `python runner.py`

### Development Workflow

The first thing you'll want to do is run `setup.bat`. This does a lot of important things:
- Sets up your rlbot installation in pip to link to your local files in this folder. Once you've done this,
running rlbot from *anywhere* on your computer will reference these local files, including the dlls, etc.
- Generates important code based on the `.fbs` message spec. Therefore it's a prerequisite for running anything.
- Installs python package dependencies.

If you're doing work that affects our `.dll` or `.exe` files, you should also be aware of:
- `copy-dlls.bat` - This copies *the debug versions* any built dlls from visual studio into the correct subdirectory in
the python source folder.
- `copy-dlls-release.bat` - This copies *the release versions* any built dlls from visual studio into the correct subdirectory in
the python source folder.

For deploying changes, please see https://github.com/RLBot/RLBot/wiki/Deploying-Changes

When you're done with development and want to get back to the official rlbot version vended from
https://pypi.org/project/rlbot/, the easiest way to do that is simply `pip uninstall rlbot`. Then
the next time you execute a bat file from one of the RLBot*Example repos, a fresh copy will be
installed from pip.

## Extras

### Community

- We have a [Discord server](https://discord.gg/VZJKWwJ) (the heart of the community, please join!)
- See tournament VODs on our [Youtube Channel](https://www.youtube.com/@RLBotOfficial).
- We also have a [subreddit](https://www.reddit.com/r/RocketLeagueBots/).
- Our machine-learning users hangs out at [RLGym](https://rlgym.org/).

### Tournaments
Our community regularly hosts tournaments. Here's the highlights from the RLBot Championship 2024.
<iframe width="560" height="315" src="https://www.youtube.com/embed/MEYizL1FQBs" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

### Psyonix Approved
RLBot was developed in collaboration with Psyonix. Thanks, Psyonix Cone!
![Thumbs up](https://github.com/drssoccer55/RLBot/blob/master/images/psyonixcone.jpg)
