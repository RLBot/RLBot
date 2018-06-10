#ifndef GAMEMESSAGES_HPP
#define GAMEMESSAGES_HPP

#include "Message.hpp"

#include "../PacketStructs/PacketStructs.hpp"

struct StartMatchMessage : public Message<StartMatchMessageType, true>
{
	MatchSettings		MatchSettings;
};

enum QuickChatPreset
{
	Information_IGotIt,
	Information_NeedBoost,
	Information_TakeTheShot,
	Information_Defending,
	Information_GoForIt,
	Information_Centering,
	Information_AllYours,
	Information_InPosition,
	Information_Incoming,
	Compliments_NiceShot,
	Compliments_GreatPass,
	Compliments_Thanks,
	Compliments_WhatASave,
	Compliments_NiceOne,
	Compliments_WhatAPlay,
	Compliments_GreatClear,
	Compliments_NiceBlock,
	Reactions_OMG,
	Reactions_Noooo,
	Reactions_Wow,
	Reactions_CloseOne,
	Reactions_NoWay,
	Reactions_HolyCow,
	Reactions_Whew,
	Reactions_Siiiick,
	Reactions_Calculated,
	Reactions_Savage,
	Reactions_Okay,
	Apologies_Cursing,
	Apologies_NoProblem,
	Apologies_Whoops,
	Apologies_Sorry,
	Apologies_MyBad,
	Apologies_Oops,
	Apologies_MyFault,
	PostGame_Gg,
	PostGame_WellPlayed,
	PostGame_ThatWasFun,
	PostGame_Rematch,
	PostGame_OneMoreGame,
	PostGame_WhatAGame,
	PostGame_NiceMoves,
	PostGame_EverybodyDance,
	MaxQuickChatPresets
};

struct SendChatMessage : public Message<SendChatMessageType, true>
{
	QuickChatPreset		QuickChatPreset;
	int					PlayerIndex;
	bool				bTeam;
};

#endif