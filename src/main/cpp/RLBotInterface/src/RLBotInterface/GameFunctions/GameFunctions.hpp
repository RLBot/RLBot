#ifndef GAMEFUNCTIONS_HPP
#define GAMEFUNCTIONS_HPP

#include "InterfaceBase/InterfaceBase.hpp"
#include "GamePacket.hpp"
#include <atomic>

namespace GameFunctions
{
	extern std::atomic_bool tcpConnected;

	#ifdef _WIN32
	extern "C" DLL_EXPORT void RLBOT_CORE_API Free(void* ptr);
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SetGameState(void* gameStateData, int size);
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartMatch(MatchSettings matchSettings);
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartMatchFlatbuffer(void* startMatchSettings, int size);
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartTcpCommunication(int port);
	#endif

	#if defined(__linux__) || defined(__APPLE__)
	extern "C" DLL_EXPORT void RLBOT_CORE_API Free(void* ptr);
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API SetGameState(void* gameStateData, int size);
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartMatch(MatchSettings matchSettings);
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartMatchFlatbuffer(void* startMatchSettings, int size);
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API StartTcpCommunication(int port);
	#endif
}

#endif