# YOU PROBABLY SHOULDN'T PULL THIS REPO

## Bot Makers Read This!

***If you just want to make a bot, you don't need to be here. Instead, start with one of these:***
 - Python - https://github.com/RLBot/RLBotPythonExample
 - Java - https://github.com/RLBot/RLBotJavaExample
 - C# (and other .NET languages) - https://github.com/RLBot/RLBotCSharpExample
 - Scratch - https://github.com/RLBot/RLBotScratchInterface
 - Rust - https://crates.io/crates/rlbot

## Framework Contributors

This repository is currently incomplete to meet the legal needs of the Psyonix API. It is missing the source code behind RLBot.exe, and a few other files. If you want to make a code change that involves RLBot.exe (or the interface dll since it's closely related), you'll need some help from someone with access to the closed repo.

We expect we'll be able to open-source everything eventually, and then this repo will be back in business.

**NOTICE:** We intend to cherry-pick any commits you make here into the closed repo. At a later date, when we have permission to open-source everything, we will **force push** the closed repo to this master branch. Your commits will still be there with proper attribution, but if you have any work in progress, it will need to be rebased at that time.

# RLBot

<p align="center">
  <img width="512" height="158" src="https://github.com/drssoccer55/RLBot/blob/master/images/RLBot.png">
</p>

[<img src="https://img.shields.io/pypi/v/rlbot.svg">](https://pypi.org/project/rlbot/)
[<img src="https://img.shields.io/bintray/v/rlbotofficial/RLBotMaven/rlbot-framework">](https://bintray.com/rlbotofficial/RLBotMaven/rlbot-framework)
[<img src="https://img.shields.io/nuget/v/RLBot.Framework">](https://www.nuget.org/packages/RLBot.Framework/)
[<img src="https://img.shields.io/crates/v/rlbot">](https://crates.io/crates/rlbot)
[<img src="https://img.shields.io/discord/348658686962696195.svg?colorB=7581dc&logo=discord&logoColor=white">](https://discord.gg/zbaAKPt)



## Framework Info

The RLBot framework helps people create bots for use in Rocket League's offline modes, just for fun.
It provides values from the game like car and ball position, and carries back button presses.
RLBot works for up to 10 bots reliably; it can be used up to 64, but can result in issues (bots disappearing after goals, spawning inside one another, etc).

### Requirements
Rocket League, Python 3.6+

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

### Wikis

There's tons of good information at https://github.com/RLBot/RLBot/wiki

### Extras

#### Community Info
 - We have a [Discord server](https://discord.gg/VZJKWwJ) (the heart of the community, please join!)
 - [We also have a subreddit.](https://www.reddit.com/r/RocketLeagueBots/)
 - We are now on v4 of RLBot so be wary of outdated information.

#### Video Example
[![Video](https://github.com/drssoccer55/RLBot/blob/master/images/vid2thumb6.JPG)](https://youtu.be/aAXe21m0vWo)

#### Tournament History
Tournament results are recorded in our [braacket league](https://braacket.com/league/rlbot).

Videos:
 - [Tournament 1 highlights](https://www.youtube.com/watch?v=PY0ggWbpsPg)
 - [Tournament 1 1v1 highlights](https://www.youtube.com/watch?v=mqXwSqy_TOw)
 - [Tournament 2 2v2 highlights](https://www.youtube.com/watch?v=U-esRgPSfn4)
 - [Full video of the first tournament, day 1](https://youtu.be/SKIw4f0ZBxE)

#### The best part
Psyonix Cone gave us a thumbs up!
![Thumbs up](https://github.com/drssoccer55/RLBot/blob/master/images/psyonixcone.jpg)
