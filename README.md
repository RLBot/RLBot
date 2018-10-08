# RLBot

<p align="center">
  <img width="512" height="158" src="https://github.com/drssoccer55/RLBot/blob/master/images/RLBot.png">
</p>

## Bot Makers Read This!

***If you just want to make a bot, you don't need to be here. Instead, start with one of these:***
 - Python - https://github.com/RLBot/RLBotPythonExample
 - Java - https://github.com/RLBot/RLBotJavaExample
 - .NET (C#, VB.NET, F# and other CLI languages) - https://github.com/RLBot/RLBotCSharpExample
 - Scratch - https://github.com/RLBot/RLBotScratchInterface
 - Rust - https://crates.io/crates/rlbot

But if you want to make improvements that help out everyone, you're in the right place!

## Framework Info

The RLBot framework helps people create bots for use in Rocket League's offline modes, just for fun.
It provides values from the game like car and ball position, and carries back button presses.
RLBot works for up to 10 bots.

### Requirements
Windows, Rocket League, Python 3.6.

### Quick Start

1. Double-click on setup.bat
2. Open up Rocket League
4. Open a terminal and execute `python runner.py`

### Useful Scripts

- `setup.bat` - This generates some code from our message spec, and also installs python package dependencies.
- `copy-dlls.bat` - This copies any built dlls from visual studio into the correct folder to speed up compile -> run time.

#### Gradle

Gradle is a build / dependency management system. You can execute various tasks with `gradlew.bat some_task`.
To use gradle, you'll need to install JDK 8 or higher.


- `publishToPyPI` - Uploads our package to [PyPI](https://pypi.org/project/rlbot/).
This is done when we want to make an update available to bot makers. See https://github.com/RLBot/RLBot/wiki/Deploying-Changes for details.
- `build` - Generates and builds Java code.
- `bintrayUpload` - Uploads Java artifacts to
[bintray](https://bintray.com/rlbotofficial/RLBotMaven/rlbot-framework). This is done when we're ready to
make an update available to java bots. To run this successfully, you will need to create a local.properties file.
  See the build.gradle file for details.

### Wikis

For more details, visit the [Setup guide](https://github.com/RLBot/RLBot/wiki/Setup-Instructions-%28current%29). When you're done, there are [more wikis](https://github.com/RLBot/RLBot/wiki) with additional information.

### Extras

#### Community Info
 - We have a [Discord server](https://discord.gg/zbaAKPt) (the heart of the community, please join!)
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
