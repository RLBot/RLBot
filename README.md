# RLBot

### Short Description
RLBot is a program to play rocket league by reading values from the process memory as input and outputing button presses to the game.  RLBot works for 1v1 exhibition games of player vs player opponent.  I use vjoy + pyvjoy + x360ce to acheive the controller simulation.  All autonomous bots that are created should be fed game values as input and perform whatever processing they wish before outputting key presses as output. The idea is to allow player made bots to be interchangeable.  One of the bots being worked on, and my initial project, requires Google Tensorflow.

#### Future Goals
Host a tournament for players to pit their created bots against each other! Need to layout official rules for this (ex. Allowed process time and make official input/output vector rules).

#### ToDo
- Sanitize player controller press vectors
- Handle overtime.  Right now I don't check time on the clock so when overtime comes up, I never reset pointers when the cars get reset.
- Handle demolitions.  This may...never happen.  When a player gets demo'd the pointers all move around and I don't know any pattern for where they go yet.
- General bug fixes as they come up

#### Quick Shoutout
Thanks to Kevin Hughes' [TensorKart](https://github.com/kevinhughes27/TensorKart) 
which helped influence and modify my original design for the project and gave me direction.

### Requirements
Windows 10, Rocket League, vjoy + pyvjoy + x360ce at least.  If you are running the tensorflow bot than definitley need (Python 3.5, Google Tensorflow).

### Longer Description

#### Video Example
[![Video](https://github.com/drssoccer55/RLBot/blob/master/images/vid2thumb4.JPG)](https://youtu.be/_heRDSm6C90)

#### Reading Values From Game
RLBot is fed values which are read from process memory or derived values from read inputs.  These values include amount of boost, xyz positional coordinates for player, ball, and opponent, rotational values, relative velocities, 
and score from the game to name a few.  Look at PlayHelper.py for all values.  The way values are read from process memory is very finicky and may require modifying pointer trails in PlayHelper.py.  I use CheatEngine to find pointer trails.  
**It is likely you will have to do some work tracking down pointers to get this program to work!**

#### Runner
Run "python runner.py" after the game is loaded and all bots and the ball are loaded on the playfield.  A GUI window should pop up after a second displaying game values.  I try my best to make sure these values are correct and the display is there so we know for sure!