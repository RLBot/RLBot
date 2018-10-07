#include <DebugHelper.hpp>

#include "GamePacket.hpp"
#include <MessageTranslation\FlatbufferTranslator.hpp>
#include "..\CallbackProcessor\SharedMemoryDefinitions.hpp"
#include "..\CallbackProcessor\CallbackProcessor.hpp"
#include <BoostUtilities\BoostUtilities.hpp>
#include <BoostUtilities\BoostConstants.hpp>

namespace GameFunctions
{
	//////////////
	// FIELD INFO
	//////////////

	static BoostUtilities::SharedMemReader flatFieldMem(BoostConstants::FieldInfoFlatName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoFlatbuffer()
	{
		return flatFieldMem.fetchData();
	}

	// Ctypes
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateFieldInfo(FieldInfo* pFieldInfo)
	{
		ByteBuffer fieldInfo = UpdateFieldInfoFlatbuffer();
		FlatbufferTranslator::translateToFieldInfoStruct(fieldInfo, pFieldInfo);
		delete[] fieldInfo.ptr;

		return RLBotCoreStatus::Success;
	}

	//////////////
	// GAME PACKET
	//////////////

	static BoostUtilities::SharedMemReader flatTickMem(BoostConstants::GameDataFlatName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketFlatbuffer()
	{
		return flatTickMem.fetchData();
	}

	// Ctypes
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateLiveDataPacket(LiveDataPacket* pLiveData)
	{
		ByteBuffer flatbuffer = UpdateLiveDataPacketFlatbuffer();
		FlatbufferTranslator::translateToStruct(flatbuffer, pLiveData);
		delete[] flatbuffer.ptr;

		return RLBotCoreStatus::Success;
	}

	///////////////
	// PHYSICS TICK
	///////////////

	static BoostUtilities::SharedMemReader physicsTickMem(BoostConstants::PhysicsTickFlatName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateRigidBodyTickFlatbuffer()
	{
		return physicsTickMem.fetchData();
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateRigidBodyTick(RigidBodyTick* rigidBodyTick)
	{
		ByteBuffer flatbuffer = UpdateRigidBodyTickFlatbuffer();
		FlatbufferTranslator::translateToRigidBodyStruct(flatbuffer, rigidBodyTick);
		delete[] flatbuffer.ptr;

		return RLBotCoreStatus::Success;
	}
}