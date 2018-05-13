#include <CapnProto\capnproto.hpp>
#include "game_data.pb.h"
#include <DebugHelper.hpp>

#include "GamePacket.hpp"

#include <chrono>
#include <thread>
#include "..\CallbackProcessor\SharedMemoryDefinitions.hpp"

namespace GameFunctions
{
	// FIELD INFO

	// Capn
	CREATE_BOOST_SHARED_MEMORY(fieldInfoShm, BoostConstants::FieldInfoSharedMemName,
		fieldInfoMutex, BoostConstants::FieldInfoMutexName)

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoCapnp()
	{
		return fetchByteBufferFromSharedMem(&fieldInfoShm, &fieldInfoMutex);
	}

	// Flat
	CREATE_BOOST_SHARED_MEMORY(fieldInfoFlatShm, BoostConstants::FieldInfoFlatSharedMemName,
		fieldInfoFlatMutex, BoostConstants::FieldInfoFlatMutexName)

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoFlatbuffer()
	{
		return fetchByteBufferFromSharedMem(&fieldInfoFlatShm, &fieldInfoFlatMutex);
	}

	// Proto
	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoProto()
	{
		ByteBuffer capnp = UpdateFieldInfoCapnp();
		return CapnConversions::capnpFieldInfoToProtobuf(capnp);
	}

	//////////////
	// GAME PACKET
	//////////////

	// Capnp
	CREATE_BOOST_SHARED_MEMORY(gameTickShm, BoostConstants::GameDataSharedMemName,
		gameTickMutex, BoostConstants::GameDataMutexName)

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketCapnp()
	{
		return fetchByteBufferFromSharedMem(&gameTickShm, &gameTickMutex);
	}

	// Flat
	CREATE_BOOST_SHARED_MEMORY(gameTickFlatShm, BoostConstants::GameDataFlatSharedMemName,
		gameTickFlatMutex, BoostConstants::GameDataFlatMutexName)

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketFlatbuffer()
	{
		return fetchByteBufferFromSharedMem(&gameTickFlatShm, &gameTickFlatMutex);
	}

	// Proto
	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketProto()
	{
		ByteBuffer capnp = UpdateLiveDataPacketCapnp();
		return CapnConversions::capnpGameTickToProtobuf(capnp);
	}

	// Ctypes
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateLiveDataPacket(LiveDataPacket* pLiveData)
	{
		ByteBuffer capnp = UpdateLiveDataPacketCapnp();
		CapnConversions::capnpGameTickToStruct(capnp, pLiveData);
		delete[] capnp.ptr;

		ByteBuffer fieldInfo = UpdateFieldInfoCapnp();
		CapnConversions::applyFieldInfoToStruct(fieldInfo, pLiveData);
		delete[] fieldInfo.ptr;

		return RLBotCoreStatus::Success;
	}
}