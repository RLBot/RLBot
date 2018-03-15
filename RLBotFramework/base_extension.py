class BaseExtension:
    """
    Extend this class to get access to extensions that are run in the game.
    """

    """an instance of SetupManager that contains helpful methods for modifying the game state."""
    setup_manager = None

    def __init__(self, setup_manager):
        self.setup_manager = setup_manager

    def onMatchEnd(self, score, stats):
        """
        Called when a match has ended.
        :param score: This contains a list of scores.  one score per a team.
        :param stats: This contains the stats as how they appear on the scoreboard at the end of the game.
        """
        pass

    def onGoalScored(self, team):
        """
        Called when a goal has been scored.
        :param team: Which team scored the goal.
        """

    def onGoalSaved(self, team):
        """
        Called when a goal has been saved/epic saved
        :param team: The team that saved the ball
        """

    def onMatchStart(self, rlbot_status):
        """
        Called when a match has started
        :return:
        """
