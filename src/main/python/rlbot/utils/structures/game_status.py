from rlbot.utils.structures.utils import create_enum_object

RLBotCoreStatus = create_enum_object(["Success",
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
                                      "InvalidRenderType",
                                      "QuickChatRateExceeded",
                                      "NotInitialized"],
                                     list_name='status_list')
