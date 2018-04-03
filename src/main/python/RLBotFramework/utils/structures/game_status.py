def create_status_object():
    status_list = ["Success",
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
     "InvalidQuickChatPreset"]
    result = lambda: None
    for i in range(len(status_list)):
        setattr(result, status_list[i], i)
    setattr(result, 'status_list', status_list)
    return result


RLBotCoreStatus = create_status_object()
