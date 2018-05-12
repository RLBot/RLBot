#ifndef GAMEFUNCTIONS_HPP
#define GAMEFUNCTIONS_HPP

#include <Messages.hpp>

#include "..\CallbackProcessor\CallbackProcessor.hpp"
#include "..\InterfaceBase\InterfaceBase.hpp"

#include "..\BoostUtilities\BoostUtilities.hpp"
#include "..\CallbackProcessor\CallbackProcessor.hpp"

// Other dll functions related to the game itself
#include "PlayerInfo.hpp"
#include "GamePacket.hpp"


#ifdef __cplusplus
extern "C"
{
#endif

	namespace GameFunctions
	{
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartMatch(MatchSettings matchSettings, CallbackFunction callback, unsigned int* pID);
        DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SetGameState(void* gameTickPacket, int protoSize, CallbackFunction callback, unsigned int* pID);
		DLL_EXPORT void RLBOT_CORE_API Free(void* ptr);
	}

#ifdef __cplusplus
}
#endif

#endif