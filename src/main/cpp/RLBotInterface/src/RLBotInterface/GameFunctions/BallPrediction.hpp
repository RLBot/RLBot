#ifndef BALLPREDICTION_HPP
#define BALLPREDICTION_HPP

#include <MessageStructs/ByteBuffer.hpp>
#include <PacketStructs/LiveDataPacket.hpp>
#include <PacketStructs/MatchDataPacket.hpp>
#include <ErrorCodes/ErrorCodes.hpp>
#include "InterfaceBase/InterfaceBase.hpp"
#include <string>

namespace BallPrediction
{
	// TODO: the core should vend a ball prediction message over TCP every time it becomes stale. For backwards compat, the interface dll
	// will be responsible for trimming off stale slices and re-packaging into a new list.
	extern "C" DLL_EXPORT ByteBuffer RLBOT_CORE_API GetBallPrediction();
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API GetBallPredictionStruct(BallPredictionPacket* pBallPrediction);
	void setBallPredictionFlatbuffer(std::string flatbuffer_content);
}

#endif