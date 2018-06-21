def create_status_object():
    status_list = ["Success",
                   "BufferOverfilled",
                   "MessageLargerThanMax",
                   "InvalidNumPlayers",
                   "InvalidBotSkill",
                   "InvalidHumanIndex",
                   "InvalidName",
                   "InvalidTeam",
                   "InvalidTeamColorID",
                   "InvalidCustomColorID",
                   "InvalidGameValues",
                   "InvalidThrottle",
                   "InvalidSteer",
                   "InvalidPitch",
                   "InvalidYaw",
                   "InvalidRoll",
                   "InvalidPlayerIndex",
                   "InvalidQuickChatPreset",
                   "InvalidRenderType"]

    def result():
        return None
    for i in range(len(status_list)):
        setattr(result, status_list[i], i)
    setattr(result, 'status_list', status_list)
    return result


RLBotCoreStatus = create_status_object()
