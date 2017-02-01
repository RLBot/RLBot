# RLBot

### Short Description
RLBot is a program which plays rocket league autonomously.  It is fed data from the game and outputs key presses to the game.  RLBot works for 1v1 exhibition games of player vs bot opponent.  RLBot uses Google Tensorflow.  Thanks to Kevin Hughes' [TensorKart](https://github.com/kevinhughes27/TensorKart) 
which helped influence and modify my original design for the project and gave me direction.

### Requirements
Python 3.5, Windows 10, Google Tensorflow, Rocket League v1.28

### Longer Description

#### Video Example
[![Video](https://github.com/drssoccer55/RLBot/blob/master/images/vid2thumb.JPG)](https://www.youtube.com/watch?v=AFxW83FZBWo)

#### Reading Values From Game
RLBot is fed values which are read from process memory or derived values from read inputs.  These values include amount of boost, xyz positional coordinates for player, ball, and opponent, rotational values, relative velocities, 
and score from the game to name a few.  Look at PlayHelper.py for all values.  The way values are read from process memory is very finicky and may require modifying pointer trails in PlayHelper.py.  I use CheatEngine to find pointer trails.

#### Recording
To train, controller presses from an xbox 360 controller are recorded along with the simultaneous game values used.  The game inputs are appended to the x.csv file and the controller inputs are appended to the y.csv file.

#### Training
train.py is used for training a model.  Command line arguments allow the specification of loading an input model and specifing the name of the saved output model.

#### Playing
play.py is used for playing.  Usually I just pause the game after the bot has spawned and countdown timer to start is around 2, alt tab out and start the play script, and then resume the game and sit back.