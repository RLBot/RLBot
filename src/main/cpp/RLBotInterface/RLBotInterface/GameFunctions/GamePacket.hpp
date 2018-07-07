#ifndef GAMEPACKET_HPP
#define GAMEPACKET_HPP

#include <MessageStructs\ByteBuffer.hpp>
#include <PacketStructs\LiveDataPacket.hpp>
#include <ErrorCodes\ErrorCodes.hpp>

#include "..\InterfaceBase\InterfaceBase.hpp"

#ifdef __cplusplus
extern "C"
{
#endif

	namespace GameFunctions
	{
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateFieldInfoFlatbuffer();
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketFlatbuffer();
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdateLiveDataPacket(LiveDataPacket* pLiveData);
	}

#ifdef __cplusplus
}
#endif

#endif