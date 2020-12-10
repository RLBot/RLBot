#ifndef PLAYERINFO_HPP
#define PLAYERINFO_HPP

#include <Messages.hpp>
#include "InterfaceBase/InterfaceBase.hpp"
#include <MessageStructs/ByteBuffer.hpp>

#ifdef __cplusplus
extern "C"
{
#endif

	namespace GameFunctions
	{
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SendQuickChat(void* quickChatMessage, int protoSize);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SendChat(QuickChatPreset quickChatPreset, int playerIndex, bool bTeam);
		DLL_EXPORT ByteBuffer RLBOT_CORE_API ReceiveChat(int botIndex, int teamIndex, int lastMessageIndex);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInput(PlayerInput playerInput, int playerIndex);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputFlatbuffer(void* playerInput, int size);
		void appendReceivedChatMessage(std::string message);
	}

#ifdef __cplusplus
}
#endif

#endif
