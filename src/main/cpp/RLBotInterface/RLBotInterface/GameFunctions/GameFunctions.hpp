#ifndef GAMEFUNCTIONS_HPP
#define GAMEFUNCTIONS_HPP

#include "..\InterfaceBase\InterfaceBase.hpp"
#include "..\CallbackProcessor\CallbackProcessor.hpp"
#include "GamePacket.hpp"

namespace GameFunctions
{
	void Initialize_GameFunctions();

	extern "C" DLL_EXPORT void RLBOT_CORE_API Free(void* ptr);
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SetGameState(void* gameStateData, int size);
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartMatch(MatchSettings matchSettings, CallbackFunction callback, unsigned int* pID);
}

#endif