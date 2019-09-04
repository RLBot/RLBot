#ifndef GAMEMESSAGES_HPP
#define GAMEMESSAGES_HPP

#include "Message.hpp"

#include "../PacketStructs/PacketStructs.hpp"

struct StartMatchMessage : public Message<StartMatchMessageType, true>
{
	MatchSettings		matchSettings;
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
	MaxPysonixQuickChatPresets,
	Custom_Toxic_WasteCPU,
	Custom_Toxic_GitGut,
	Custom_Toxic_DeAlloc,
	Custom_Toxic_404NoSkill,
	Custom_Toxic_CatchVirus,
	Custom_Useful_Passing,
	Custom_Useful_Faking,
	Custom_Useful_Demoing,
	Custom_Useful_Bumping,
	Custom_Compliments_TinyChances,
	Custom_Compliments_SkillLevel,
	Custom_Compliments_proud,
	Custom_Compliments_GC,
	Custom_Compliments_Pro,
	MaxQuickChatPresets
};

struct SendChatMessage : public Message<SendChatMessageType, true>
{
	QuickChatPreset		quickChatPreset;
	int					playerIndex;
	bool				bTeam;
};

#endif