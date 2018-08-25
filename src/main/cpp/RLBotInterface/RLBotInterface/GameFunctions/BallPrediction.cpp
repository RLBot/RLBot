#include "BallPrediction.hpp"
#include <BoostUtilities\BoostUtilities.hpp>
#include <BoostUtilities\BoostConstants.hpp>

namespace BallPrediction
{
	extern "C" ByteBuffer RLBOT_CORE_API FetchBallPrediction()
	{
		static BoostUtilities::SharedMemReader ballPredictionMem(BoostConstants::BallPredictionName);
		return ballPredictionMem.fetchData();
	}
}