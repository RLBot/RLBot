# RLBot

### Short Description
RLBot is a program to play rocket league by reading values from the process memory as input and outputing button presses to the game.  RLBot "works"(if your standards are low at the moment) for 1v1 exhibition games of player vs bot opponent.  
The current goal of the project is to create a bot which can play the game autonomously.  All autonomous bots that are created should be fed game values as input and perform whatever processing they wish before outputting 
key presses as output. The idea is to allow player made bots to be interchangeable.  One of the bots being worked, and my initial project, requires Google Tensorflow.

#### Future Goals
In the future hopefully I will be able to pit player created programs against each other and host a tournament of sorts.  There are a couple tricky things to work out first.  One thing is Rocket League does not allow two keyboard player inputs.  
I will likely have to emulate 2 controllers to get this part to work.  Another thing would be defining what inputs will be given officially.  One thing to consider here is blue's target and orange's target are at different places so the player needs to know what color they are playing as.  
Another thing is having a limit on allowed process time.

#### Quick Shoutout
Thanks to Kevin Hughes' [TensorKart](https://github.com/kevinhughes27/TensorKart) 
which helped influence and modify my original design for the project and gave me direction.

### Requirements
Windows 10, Rocket League at least.  If you are running the tensorflow bot than definitley need (Python 3.5, Google Tensorflow).

### Longer Description

#### Video Example
[![Video](https://github.com/drssoccer55/RLBot/blob/master/images/vid2thumb2.JPG)](https://www.youtube.com/watch?v=a-kyXoxCQ3k)

#### Reading Values From Game
RLBot is fed values which are read from process memory or derived values from read inputs.  These values include amount of boost, xyz positional coordinates for player, ball, and opponent, rotational values, relative velocities, 
and score from the game to name a few.  Look at PlayHelper.py for all values.  The way values are read from process memory is very finicky and may require modifying pointer trails in PlayHelper.py.  I use CheatEngine to find pointer trails.  
**It is likely you will have to do some work tracking down pointers to get this program to work!**

#### Runner
Run "python runner.py" after the game is loaded and all bots and the ball are loaded on the playfield.  A GUI window should pop up after a second displaying game values.  I try my best to make sure these values are correct but it is buggy at the moment.