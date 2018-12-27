from rlbot.base_extension import BaseExtension

class TrainingExtension(BaseExtension):
    """
    This extension is intended to forward events to the current Training Exercise.
    But currently it just is coded to show the details of the events.
    """
    def __init__(self, setup_manager):
        super().__init__(setup_manager)

    def onMatchEnd(self, score, stats):
        print('onMatchEnd()')
        print(f'score {score}')
        print(f'score._class {score.__class__}')
        print(f'stats {stats}')
        print(f'stats._class {stats.__class__}')

    def onGoalScored(self, team):
        print('onGoalScored()')
        print(f'team {team}')
        print(f'team._class {team.__class__}')

    def onGoalSaved(self, team):
        print('onGoalSaved()')
        print(f'team {team}')
        print(f'team._class {team.__class__}')

    def onMatchStart(self, rlbot_status):
        print('onMatchStart()')
        print(f'rlbot_status {rlbot_status}')
        print(f'rlbot_status._class {rlbot_status.__class__}')
