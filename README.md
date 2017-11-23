# RLBot

<p align="center">
  <img width="651" height="630" src="https://github.com/drssoccer55/RLBot/blob/master/images/RLBot_logo.png">
</p>

### Short Description
RLBot is a framework to create bots to play rocket league that reads values from the game and outputs button presses to the game. RLBot works for up to 10 bots.

#### ToDo
- General bug fixes as they come up

### Requirements
Windows, Rocket League, Python 3. If you are running my tensorflow bot than you definitley need (Python 3.5, Google Tensorflow).

### Longer Description

#### Good Information
For the most up to date guides, please check the wikis on this github repo. [Please join the discord as well.](https://discord.gg/zbaAKPt) [We also have a subreddit.](https://www.reddit.com/r/RocketLeagueBots/) We are now on v3 of RLBot so you may see some old information that no longer applies.

#### Video Example
[![Video](https://github.com/drssoccer55/RLBot/blob/master/images/vid2thumb6.JPG)](https://youtu.be/aAXe21m0vWo)

#### Reading Values From Game
RLBot is fed values from an injected dll. These values include amount of boost, xyz positional coordinates for player, ball, and opponent, rotational values, and score from the game to name a few.

#### Runner
Inject the dll into RocketLeague first (only need to do this step once each time you open rocketleague). Run "python runner.py" at player select screen with configurations specified in rlbot.cfg and it will automatically start the game.

#### Tournament History
Inagural Tournament Video Day 1 (Psyonix Cone gave us a thumbs up!):
[![Video](https://github.com/drssoccer55/RLBot/blob/master/images/psyonixcone.jpg)](https://youtu.be/SKIw4f0ZBxE)