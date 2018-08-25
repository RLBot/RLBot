#include "PredictionService.hpp"
#include <math.h>

namespace BallPrediction {


	std::list<BallSlice>* PredictionService::updatePrediction(BallSlice inputSlice)
	{

		BallSlice baseSlice;

		if (currentPredictionStillValid(inputSlice)) {

			baseSlice = prediction.back();

			// Trim off the parts of the old prediction that are now in the past.
			while (prediction.front().gameSeconds < inputSlice.gameSeconds) {
				prediction.pop_front();
			}

			if (prediction.front().gameSeconds > inputSlice.gameSeconds) {
				// Add back the current slice to ensure that currentPredictionStillValid will work next time,
				// because the prediction time range needs to include the gameSeconds.
				prediction.push_front(inputSlice);
			}
		}
		else {
			prediction.clear();
			prediction.push_back(inputSlice);
			baseSlice = inputSlice;
		}

		ball.x = baseSlice.Location;
		ball.v = baseSlice.Velocity;
		ball.w = baseSlice.AngularVelocity;

		float predictionSeconds = baseSlice.gameSeconds;
		while (prediction.size() < expectedNumSlices) {
			ball.step(stepInterval);
			predictionSeconds += stepInterval;

			BallSlice predicted;
			predicted.Location = ball.x;
			predicted.Velocity = ball.v;
			predicted.AngularVelocity = ball.w;
			predicted.gameSeconds = predictionSeconds;

			prediction.push_back(predicted);
		}

		return &prediction;
	}

	bool PredictionService::currentPredictionStillValid(BallSlice currentBallPosition)
	{
		BallSlice* predictedSlice = new BallSlice();
		bool valid = false;
		if (expectedBallPosition(currentBallPosition.gameSeconds, predictedSlice)) {
			
			vec3 toPredicted = predictedSlice->Location - currentBallPosition.Location;
			float error = dot(toPredicted, toPredicted);
			if (error < 12) {
				valid = true;
			}
			else {
				// printf("Expected ball position is %f off by dot product.\n", error);
			}
		}

		delete predictedSlice;
		return valid;
		
	}

	bool PredictionService::expectedBallPosition(float gameSeconds, BallSlice* outputSlice)
	{
		if (prediction.empty()) {
			printf("Current prediction is empty.\n");
			return false;
		}

		if (prediction.front().gameSeconds > gameSeconds || prediction.back().gameSeconds <= gameSeconds) {
			printf("GameSeconds is out of bounds. Front seconds %f, back seconds %f\n", prediction.front().gameSeconds, prediction.back().gameSeconds);
			return false;
		}

		float predictionStartTime = prediction.front().gameSeconds;
		float secondsIntoPrediction = gameSeconds - predictionStartTime;
		int searchStart = (int) (secondsIntoPrediction / stepInterval);


		std::list<BallSlice>::iterator it = prediction.begin();
		std::advance(it, searchStart);
		BallSlice sliceBefore = *it;
		std::advance(it, 1);
		BallSlice sliceAfter = *it;
		while (sliceAfter.gameSeconds < gameSeconds) {
			std::advance(it, 1);
			sliceBefore = sliceAfter;
			sliceAfter = *it;
		}

		float interpolationFactor = (gameSeconds - sliceBefore.gameSeconds) / (sliceAfter.gameSeconds - sliceBefore.gameSeconds);
		float complementaryFactor = 1 - interpolationFactor;

		outputSlice->Location = (sliceBefore.Location * complementaryFactor + sliceAfter.Location * interpolationFactor);
		outputSlice->Velocity = (sliceBefore.Velocity * complementaryFactor + sliceAfter.Velocity * interpolationFactor);
		outputSlice->AngularVelocity = (sliceBefore.AngularVelocity * complementaryFactor + sliceAfter.AngularVelocity * interpolationFactor);
		outputSlice->gameSeconds = gameSeconds;

		return true;
	}

}