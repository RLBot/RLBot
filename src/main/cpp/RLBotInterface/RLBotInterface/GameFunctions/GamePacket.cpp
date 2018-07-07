#include "GamePacket.hpp"

#include <BoostUtilities\BoostUtilities.hpp>
#include <BoostUtilities\BoostConstants.hpp>
#include <MessageTranslation\FlatbufferTranslator.hpp>

namespace GameFunctions
{
	// FIELD INFO
	static BoostUtilities::SharedMemReader flatFieldMem(BoostConstants::FieldInfoFlatName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoFlatbuffer()
	{
		return flatFieldMem.fetchData();
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

		ByteBuffer fieldInfo = UpdateFieldInfoFlatbuffer();
		FlatbufferTranslator::applyFieldInfoToStruct(fieldInfo, pLiveData);
		delete[] fieldInfo.ptr;

		return RLBotCoreStatus::Success;
	}
}