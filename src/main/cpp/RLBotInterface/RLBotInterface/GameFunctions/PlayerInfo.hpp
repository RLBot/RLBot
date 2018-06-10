#ifndef PLAYERINFO_HPP
#define PLAYERINFO_HPP

#include <Messages.hpp>

#include "..\CallbackProcessor\CallbackProcessor.hpp"
#include "..\InterfaceBase\InterfaceBase.hpp"

#include <BoostUtilities\BoostUtilities.hpp>


#ifdef __cplusplus
extern "C"
{
#endif

	namespace GameFunctions
	{
		RLBotCoreStatus checkQuickChatPreset(QuickChatPreset quickChatPreset);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SendQuickChat(void* quickChatMessage, int protoSize);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SendChat(QuickChatPreset quickChatPreset, int playerIndex, bool bTeam, CallbackFunction callback = nullptr, unsigned int* pID = nullptr);

		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInput(PlayerInput playerInput, int playerIndex);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputFlatbuffer(void* playerInput, int size);
	}

#ifdef __cplusplus
}
#endif

#endif
