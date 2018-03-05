class RLBotException(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "An error occurred attempting to set RLBot configuration on the dll side"
        super(RLBotException, self).__init__(msg)
        self.error_dict = {1: InvalidNumPlayerError(), 2: InvalidBotSkillError(), 3: InvalidPlayerIndexError(),
                           4: InvalidName(), 5: InvalidTeam, 6: InvalidTeamColor(), 7: InvalidCustomColor,
                           8: InvalidGameValues, 9: InvalidThrottle, 10: InvalidSteer, 11: InvalidPitch,
                           12: InvalidRoll, 13: InvalidSteer}

    def raise_exception_from_error_code(self, error_code):
        try:
            return self.error_dict[error_code]
        except KeyError:
            return self


class InvalidNumPlayerError(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid number of cars specified in configuration")


class InvalidBotSkillError(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid bot skill specified in configuration")


class InvalidPlayerIndexError(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid player index")


class InvalidName(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid name error. Python side was supposed to properly sanitize this!")


class InvalidTeam(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid team specified in configuration")


class InvalidTeamColor(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid team color specified")


class InvalidCustomColor(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid custom color specified")


class InvalidGameValues(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid game values")

class InvalidThrottle(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid throttle input")

class InvalidSteer(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid steer input")

class InvalidPitch(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid pitch input")


class InvalidYaw(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid yaw input")


class InvalidRoll(RLBotException):
    def __init__(self):
        super(RLBotException, self).__init__("Invalid roll input")