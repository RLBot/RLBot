
# TODO: bikeshed about testing frameworks
# TODO: write more tests. eg. "atba should hit the ball"

def test_sufficient_data(history):
    assert len(history) > 100

def test_tick_rate(history):
    ''' Checks that we're consistently running at 60 ticks/s'''
    fps = 60  # I know it's not frames but I find it easier to read than tps.

    def get_time(history_item):
        return history_item.game_tick_proto.GameInfo().SecondsElapsed()

    def is_admissible(history_item):
        return history_item.game_tick_proto.GameInfo().IsRoundActive()

    intervals = [
        get_time(history[i+1]) - get_time(history[i])
        for i in range(len(history)-1)
        if is_admissible(history[i+1]) and is_admissible(history[i])
    ]
    assert len(intervals) > 10, "Didn't get enough admissible game_tick_proto's. (got {})".format(len(intervals))

    def is_interval_acceptable(interval):
        acceptable_margin = 0.1 / fps
        return abs(interval - 1./fps) < acceptable_margin
    acceptables = [ is_interval_acceptable(interval) for interval in intervals ]
    average_interval = sum(intervals) / len(intervals)
    proportion_acceptable = sum(acceptables) / len(acceptables)

    tick_rate_is_good = proportion_acceptable >= 0.98

    # print the intervals so we can plot them in a spreasheet or whatever.
    # if not tick_rate_is_good:
    #     for i in intervals:
    #         print (i)

    assert tick_rate_is_good, 'Not running at a consistent {} fps. Only {} out of {} frames were on time ({} %). average_interval={:3f} ({:3f} fps)'.format(
        fps, sum(acceptables), len(acceptables), proportion_acceptable*100, average_interval, 1/average_interval
    )
