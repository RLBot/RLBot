These instructions are intended for a tournament organizer. In theory, you're reading this because
you've just unzipped something. If that's not your situation, go look at README.md
instead.

1. Install Java 8.
2. Run `pip install grpcio` on the command line (one time setup).
3. Copy the included `.py` and `.cfg` file(s) to your RLBot directory, as you would do with a plain python bot.
4. Modify rlbot.cfg and set up the match as you normally would.
3. Before (or after) running `python runner.py`, double click on the `.bat` file included in
the bin directory. 


You only need to run a single instance of the `.bat`, and it can handle all the bots configured
to run on its port in the whole match, even on opposite teams.


Advanced:

- It's fine to close and restart the `.bat` while runner.py is active.
- You can also run the `.bat` on the command line to see stack traces for debugging purposes.