#ifndef PLAYERINFO_HPP
#define PLAYERINFO_HPP

#include <Messages.hpp>

#include "..\InterfaceBase\InterfaceBase.hpp"

#include <BoostUtilities\BoostUtilities.hpp>

#ifdef __cplusplus
extern "C"
{
#endif

	namespace GameFunctions
	{
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SendQuickChat(void* quickChatMessage, int protoSize);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInput(const PlayerInput& playerInput, int playerIndex);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputFlatbuffer(void* playerInput, int size);
	}

#ifdef __cplusplus
}
#endif

#endif
