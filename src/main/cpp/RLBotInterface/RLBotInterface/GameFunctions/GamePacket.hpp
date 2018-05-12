#ifndef GAMEPACKET_HPP
#define GAMEPACKET_HPP

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
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketProto();
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketCapnp();
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketFlatbuffer();
	}

#ifdef __cplusplus
}
#endif

#endif