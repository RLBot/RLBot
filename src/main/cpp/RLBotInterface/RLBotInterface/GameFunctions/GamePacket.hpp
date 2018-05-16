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
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateFieldInfoCapnp();
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateFieldInfoFlatbuffer();
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateFieldInfoProto();

		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketCapnp();
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketFlatbuffer();
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketProto();
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdateLiveDataPacket(LiveDataPacket* pLiveData);
	}

#ifdef __cplusplus
}
#endif

#endif