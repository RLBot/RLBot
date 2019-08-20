#ifndef BALLPREDICTION_HPP
#define BALLPREDICTION_HPP

#include <MessageStructs\ByteBuffer.hpp>
#include <PacketStructs\LiveDataPacket.hpp>
#include <PacketStructs\MatchDataPacket.hpp>
#include <ErrorCodes\ErrorCodes.hpp>
#include "..\InterfaceBase\InterfaceBase.hpp"

namespace BallPrediction
{
	extern "C" DLL_EXPORT ByteBuffer RLBOT_CORE_API GetBallPrediction();
	extern "C" DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API GetBallPredictionStruct(BallPredictionPacket* pBallPrediction);
}

#endif