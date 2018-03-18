
# TODO: bikeshed about testing frameworks
# TODO: write more tests. eg. "atba should hit the ball"

def test_sufficient_data(history):
    assert len(history) > 100

def test_tick_rate(history):
    ''' Checks that we're consistently running at 60 ticks/s'''
    fps = 60  # I know it's not frames but I find it easier to read than tps.
    times = [ item.game_tick_proto.game_info.seconds_elapsed for item in history ]
    intervals = [ times[i+1] - time for i, time in enumerate(times[:-1]) ]
    def is_interval_acceptable(interval):
        acceptable_margin = 0.1 / fps
        return abs(interval - 1./fps) < acceptable_margin
    acceptables = [ is_interval_acceptable(interval) for interval in intervals ]
    proportion_acceptable = sum(acceptables) / len(acceptables)
    assert proportion_acceptable >= 0.98, 'Not running at a consistent {} fps. Only {} out of {} frames were on time ({} %)'.format(fps, sum(acceptables), len(acceptables), proportion_acceptable*100)
