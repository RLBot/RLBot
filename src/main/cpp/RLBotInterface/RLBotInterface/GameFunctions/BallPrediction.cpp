#include <DebugHelper.hpp>
#include <Messages.hpp>

#include "BallPrediction.hpp"
#include <MessageTranslation\FlatbufferTranslator.hpp>
#include "..\CallbackProcessor\SharedMemoryDefinitions.hpp"
#include "..\CallbackProcessor\CallbackProcessor.hpp"
#include <BoostUtilities\BoostUtilities.hpp>
#include <BoostUtilities\BoostConstants.hpp>

namespace BallPrediction
{
	BoostUtilities::SharedMemReader* pBallPredictionMem = nullptr;

	extern "C" ByteBuffer RLBOT_CORE_API GetBallPrediction()
	{
		if (!MutexUtilities::IsBallPredictionServiceRunning())
		{
			ByteBuffer empty;
			empty.ptr = new char[1]; // Arbitrary valid pointer to an array. We'll be calling delete[] on this later.
			empty.size = 0;
			return empty;
		}
		else if (!pBallPredictionMem)
			pBallPredictionMem = new BoostUtilities::SharedMemReader(BoostConstants::BallPredictionName);

		return pBallPredictionMem->fetchData();
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