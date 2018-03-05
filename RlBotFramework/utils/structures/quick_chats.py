def get_quick_chats():
    quick_chat_list = ["Information_IGotIt",
                       "Information_NeedBoost",
                       "Information_TakeTheShot",
                       "Information_Defending",
                       "Information_GoForIt",
                       "Information_Centering",
                       "Information_AllYours",
                       "Information_InPosition",
                       "Information_Incoming",
                       "Compliments_NiceShot",
                       "Compliments_GreatPass",
                       "Compliments_Thanks",
                       "Compliments_WhatASave",
                       "Compliments_NiceOne",
                       "Compliments_WhatAPlay",
                       "Compliments_GreatClear",
                       "Compliments_NiceBlock",
                       "Reactions_OMG",
                       "Reactions_Noooo",
                       "Reactions_Wow",
                       "Reactions_CloseOne",
                       "Reactions_NoWay",
                       "Reactions_HolyCow",
                       "Reactions_Whew",
                       "Reactions_Siiiick",
                       "Reactions_Calculated",
                       "Reactions_Savage",
                       "Reactions_Okay",
                       "Apologies_Cursing",
                       "Apologies_NoProblem",
                       "Apologies_Whoops",
                       "Apologies_Sorry",
                       "Apologies_MyBad",
                       "Apologies_Oops",
                       "Apologies_MyFault",
                       "PostGame_Gg",
                       "PostGame_WellPlayed",
                       "PostGame_ThatWasFun",
                       "PostGame_Rematch",
                       "PostGame_OneMoreGame",
                       "PostGame_WhatAGame",
                       "PostGame_NiceMoves",
                       "PostGame_EverybodyDance"]
    result = lambda: None
    for i in range(len(quick_chat_list)):
        setattr(result, quick_chat_list[i], i)
    setattr(result, 'quick_chat_list', quick_chat_list)
    setattr(result, 'CHAT_NONE', -1)
    setattr(result, 'CHAT_EVERYONE', False)
    setattr(result, 'CHAT_TEAM_ONLY', True)
    return result


QuickChats = get_quick_chats()
