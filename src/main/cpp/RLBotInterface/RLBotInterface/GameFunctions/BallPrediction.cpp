#include <DebugHelper.hpp>

#include "BallPrediction.hpp"
#include <MessageTranslation\FlatbufferTranslator.hpp>
#include "..\CallbackProcessor\SharedMemoryDefinitions.hpp"
#include "..\CallbackProcessor\CallbackProcessor.hpp"
#include <BoostUtilities\BoostUtilities.hpp>
#include <BoostUtilities\BoostConstants.hpp>

namespace BallPrediction
{
	extern "C" ByteBuffer RLBOT_CORE_API GetBallPrediction()
	{
		static BoostUtilities::SharedMemReader ballPredictionMem(BoostConstants::BallPredictionName);
		return ballPredictionMem.fetchData();
	}

	// Ctypes
	extern "C" RLBotCoreStatus RLBOT_CORE_API GetBallPredictionStruct(BallPredictionPacket* pBallPrediction)
	{
		ByteBuffer flatbuffer = GetBallPrediction();
		FlatbufferTranslator::translateToPrediction(flatbuffer, pBallPrediction);
		delete[] flatbuffer.ptr;

		return RLBotCoreStatus::Success;
	}
}