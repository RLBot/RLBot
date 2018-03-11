#ifndef GAMEFUNCTIONS_HPP
#define GAMEFUNCTIONS_HPP

#include <Messages.hpp>

#include "..\CallbackProcessor\CallbackProcessor.hpp"
#include "..\InterfaceBase\InterfaceBase.hpp"

#ifdef ENABLE_PROTO
#include <game_data.pb.h>
#include "..\ProtoConversions\ProtoConversions.hpp"
#endif

#ifdef __cplusplus
extern "C"
{
#endif

	namespace GameFunctions
	{
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdateLiveDataPacket(LiveDataPacket* pLiveData);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdateMatchDataPacket(MatchDataPacket* pMatchData);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartMatch(PlayerConfiguration playerConfiguration[CONST_MaxPlayers], int numPlayers, CallbackFunction callback = nullptr, unsigned int* pID = nullptr);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInput(const PlayerInput& playerInput, int playerIndex);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SendChat(QuickChatPreset quickChatPreset, int playerIndex, bool bTeam, CallbackFunction callback = nullptr, unsigned int* pID = nullptr);

#ifdef ENABLE_PROTO
		DLL_EXPORT void* RLBOT_CORE_API UpdateLiveDataPacketProto();
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputProto(void* playerInput);
#endif
	}

#ifdef __cplusplus
}
#endif

#endif