#ifndef ERRORCODES_HPP
#define ERRORCODES_HPP

//enum RLBotCoreError
//{
//	NoError,
//	InvalidNumPlayers,
//	InvalidBotSkill,
//	InvalidPlayerIndex,
//	InvalidName,
//	InvalidTeam,
//	InvalidTeamColorID,
//	InvalidCustomColorID,
//	InvalidGameValues,
//	InvalidThrottle,
//	InvalidSteer,
//	InvalidPitch,
//	InvalidYaw,
//	InvalidRoll
//};

enum RLBotCoreStatus
{
	Success,
	BufferOverfilled,
	MessageLargerThanMax,
	InvalidNumPlayers,
	InvalidBotSkill,
	InvalidHumanIndex,
	InvalidName,
	InvalidTeam,
	InvalidTeamColorID,
	InvalidCustomColorID,
	InvalidGameValues,
	InvalidThrottle,
	InvalidSteer,
	InvalidPitch,
	InvalidYaw,
	InvalidRoll,
	InvalidPlayerIndex,
	InvalidQuickChatPreset,
	InvalidRenderType,
	QuickChatRateExceeded
};

#endif