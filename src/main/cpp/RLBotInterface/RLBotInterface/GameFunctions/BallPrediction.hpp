#ifndef BALLPREDICTION_HPP
#define BALLPREDICTION_HPP

#include <MessageStructs\ByteBuffer.hpp>
#include <PacketStructs\LiveDataPacket.hpp>
#include <PacketStructs\MatchDataPacket.hpp>
#include <ErrorCodes\ErrorCodes.hpp>
#include "..\InterfaceBase\InterfaceBase.hpp"


#ifdef __cplusplus
extern "C"
{
#endif

	namespace BallPrediction
	{
		DLL_EXPORT ByteBuffer RLBOT_CORE_API GetBallPrediction();
		DLL_EXPORT RLBotCoreStatus RLBOT_CORE_API GetBallPredictionStruct(BallPredictionPacket* pBallPrediction);
	}

#ifdef __cplusplus
}
#endif

#endif