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
	static boost::interprocess::shared_memory_object fieldInfoShm(
		boost::interprocess::open_only, BoostConstants::FieldInfoSharedMemName, boost::interprocess::read_only);

	static boost::interprocess::named_sharable_mutex fieldInfoMutex(
		boost::interprocess::open_only, BoostConstants::FieldInfoMutexName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoCapnp()
	{
		return fetchByteBufferFromSharedMem(&fieldInfoShm, &fieldInfoMutex);
	}

	// Flat
	static boost::interprocess::shared_memory_object fieldInfoFlatShm(
		boost::interprocess::open_only, BoostConstants::FieldInfoFlatSharedMemName, boost::interprocess::read_only);

	static boost::interprocess::named_sharable_mutex fieldInfoFlatMutex(
		boost::interprocess::open_only, BoostConstants::FieldInfoFlatMutexName);

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


	// Game Packet
	 

	// Capnp
	static boost::interprocess::shared_memory_object gameTickShm(
		boost::interprocess::open_only, BoostConstants::GameDataSharedMemName, boost::interprocess::read_only);

	static boost::interprocess::named_sharable_mutex gameTickMutex(
		boost::interprocess::open_only, BoostConstants::GameDataMutexName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketCapnp()
	{
		return fetchByteBufferFromSharedMem(&gameTickShm, &gameTickMutex);
	}

	// Flat
	static boost::interprocess::shared_memory_object gameTickFlatShm(
		boost::interprocess::open_only, BoostConstants::GameDataFlatSharedMemName, boost::interprocess::read_only);

	static boost::interprocess::named_sharable_mutex gameTickFlatMutex(
		boost::interprocess::open_only, BoostConstants::GameDataFlatMutexName);

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