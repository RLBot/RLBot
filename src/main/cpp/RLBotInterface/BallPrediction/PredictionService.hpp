#pragma once

#include "inc\vec.h"
#include "inc\Ball.h"
#include <list>

namespace BallPrediction {

	struct BallSlice {
		vec3 Location;
		vec3 Velocity;
		vec3 AngularVelocity;
		float gameSeconds;
	};


	class PredictionService {
	private:
		const float secondsToPredict;
		const float stepInterval;
		const int expectedNumSlices;
		std::list<BallSlice> prediction;
		bool currentPredictionStillValid(BallSlice currentBallPosition);
		bool expectedBallPosition(float gameSeconds, BallSlice* outputSlice);
		Ball ball;
	public:
		PredictionService(float secondsToPredict, float stepInterval) : 
			prediction(), 
			secondsToPredict(secondsToPredict), 
			stepInterval(stepInterval),
			expectedNumSlices(secondsToPredict / stepInterval),
			ball()
		{ 
		}
		std::list<BallSlice>* updatePrediction(BallSlice slice);
	};

}