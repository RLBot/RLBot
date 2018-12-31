#include <DebugHelper.hpp>

#include "GamePacket.hpp"
#include <MessageTranslation\FlatbufferTranslator.hpp>
#include "..\CallbackProcessor\SharedMemoryDefinitions.hpp"
#include "..\CallbackProcessor\CallbackProcessor.hpp"
#include <BoostUtilities\BoostUtilities.hpp>
#include <BoostUtilities\BoostConstants.hpp>

namespace GameFunctions
{
	BoostUtilities::SharedMemReader* pFlatFieldMem = nullptr;
	BoostUtilities::SharedMemReader* pFlatTickMem = nullptr;
	BoostUtilities::SharedMemReader* pPhysicsTickMem = nullptr;

	void Initialize_GamePacket()
	{
		pFlatFieldMem = new BoostUtilities::SharedMemReader(BoostConstants::FieldInfoFlatName);
		pFlatTickMem = new BoostUtilities::SharedMemReader(BoostConstants::GameDataFlatName);
		pPhysicsTickMem = new BoostUtilities::SharedMemReader(BoostConstants::PhysicsTickFlatName);
	}

	//////////////
	// FIELD INFO
	//////////////

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoFlatbuffer()
	{
		return pFlatFieldMem->fetchData();
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

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketFlatbuffer()
	{
		return pFlatTickMem->fetchData();
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

	extern "C" ByteBuffer RLBOT_CORE_API UpdateRigidBodyTickFlatbuffer()
	{
		return pPhysicsTickMem->fetchData();
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateRigidBodyTick(RigidBodyTick* rigidBodyTick)
	{
		ByteBuffer flatbuffer = UpdateRigidBodyTickFlatbuffer();
		FlatbufferTranslator::translateToRigidBodyStruct(flatbuffer, rigidBodyTick);
		delete[] flatbuffer.ptr;

		return RLBotCoreStatus::Success;
	}
}