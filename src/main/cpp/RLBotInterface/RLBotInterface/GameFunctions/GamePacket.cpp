#include <CapnProto\capnproto.hpp>
#include "game_data.pb.h"
#include <DebugHelper.hpp>

#include "GamePacket.hpp"

#include "..\CallbackProcessor\SharedMemoryDefinitions.hpp"
#include <BoostUtilities\BoostUtilities.hpp>
#include <BoostUtilities\BoostConstants.hpp>

namespace GameFunctions
{
	// FIELD INFO

	// Capn
	static BoostUtilities::SharedMemReader capnFieldMem(BoostConstants::FieldInfoName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoCapnp()
	{
		return capnFieldMem.fetchData();
	}

	// Flat
	static BoostUtilities::SharedMemReader flatFieldMem(BoostConstants::FieldInfoFlatName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoFlatbuffer()
	{
		return flatFieldMem.fetchData();
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
	static BoostUtilities::SharedMemReader capnTickMem(BoostConstants::GameDataName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketCapnp()
	{
		return capnTickMem.fetchData();
	}

	// Flat
	static BoostUtilities::SharedMemReader flatTickMem(BoostConstants::GameDataFlatName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketFlatbuffer()
	{
		return flatTickMem.fetchData();
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