#ifndef GAMEFUNCTIONS_HPP
#define GAMEFUNCTIONS_HPP

#include <Messages.hpp>

#include "..\CallbackProcessor\CallbackProcessor.hpp"
#include "..\InterfaceBase\InterfaceBase.hpp"


#ifdef __cplusplus
extern "C"
{
#endif

	namespace GameFunctions
	{
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdateLiveDataPacket(LiveDataPacket* pLiveData);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdateMatchDataPacket(MatchDataPacket* pMatchData);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartMatch(MatchSettings matchSettings, CallbackFunction callback, unsigned int* pID);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInput(const PlayerInput& playerInput, int playerIndex);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SendChat(QuickChatPreset quickChatPreset, int playerIndex, bool bTeam, CallbackFunction callback = nullptr, unsigned int* pID = nullptr);

        DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketProto();
        DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SetGameState(void* gameTickPacket, int protoSize, CallbackFunction callback, unsigned int* pID);
        DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputProto(void* controllerState, int protoSize);
		DLL_EXPORT void RLBOT_CORE_API Free(void* ptr);
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketCapnp();
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputCapnp(void* controllerState, int protoSize);
	}

#ifdef __cplusplus
}
#endif

#endif