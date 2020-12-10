#ifndef GAMEPACKET_HPP
#define GAMEPACKET_HPP

#include <MessageStructs/ByteBuffer.hpp>
#include <PacketStructs/LiveDataPacket.hpp>
#include <PacketStructs/MatchDataPacket.hpp>
#include <PacketStructs/RigidBodyStructs.hpp>
#include <ErrorCodes/ErrorCodes.hpp>
#include "InterfaceBase/InterfaceBase.hpp"
#include <string>


#ifdef __cplusplus
extern "C"
{
#endif

	namespace GameFunctions
	{
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateFieldInfoFlatbuffer();
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdateFieldInfo(FieldInfo* pFieldInfo);
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketFlatbuffer();
		DLL_EXPORT ByteBuffer RLBOT_CORE_API FreshLiveDataPacketFlatbuffer(int timeoutMillis, int key);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdateLiveDataPacket(LiveDataPacket* pLiveData);
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API FreshLiveDataPacket(LiveDataPacket* pLiveData, int timeoutMillis, int key);
		DLL_EXPORT ByteBuffer RLBOT_CORE_API UpdateRigidBodyTickFlatbuffer();
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API UpdateRigidBodyTick(RigidBodyTick* rigidBodyTick);
		DLL_EXPORT ByteBuffer RLBOT_CORE_API GetMatchSettings();
		void setGameTickPacketFlatbuffer(std::string flatbuffer_content);
		void setFieldInfoPacketFlatbuffer(std::string flatbuffer_content);
		void setMatchSettingsFlatbuffer(std::string flatbuffer_content);
		bool hasFieldData();
	}

#ifdef __cplusplus
}
#endif

#endif