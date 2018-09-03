#ifndef GAMEFUNCTIONS_HPP
#define GAMEFUNCTIONS_HPP

#include "..\InterfaceBase\InterfaceBase.hpp"
#include "..\CallbackProcessor\CallbackProcessor.hpp"
#include "GamePacket.hpp"


#ifdef __cplusplus
extern "C"
{
#endif

	namespace GameFunctions
	{
		DLL_EXPORT void RLBOT_CORE_API Free(void* ptr);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SetGameState(void* gameStateData, int size);

		bool isValidName(wchar_t* pName);
		RLBotCoreStatus checkPlayerConfiguration(PlayerConfiguration playerConfiguration[CONST_MaxPlayers], int numPlayers);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartMatch(MatchSettings matchSettings, CallbackFunction callback, unsigned int* pID);
	}

#ifdef __cplusplus
}
#endif

#endif