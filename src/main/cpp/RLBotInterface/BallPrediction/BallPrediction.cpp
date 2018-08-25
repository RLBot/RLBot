// BallPrediction.cpp : Defines the entry point for the console application.
//

#include <stdio.h>
#include <chrono>
#include <thread>
#include <csignal>
#include "PredictionService.hpp"
#include <GameFunctions\GameFunctions.hpp>
#include <rlbot_generated.h>
#include <BoostUtilities\BoostUtilities.hpp>
#include <BoostUtilities\BoostConstants.hpp>


vec3 convertVec(const rlbot::flat::Vector3* vec)
{
	return vec3{ vec->x(), vec->y(), vec->z() };
}

rlbot::flat::Vector3 convertVec(vec3 vec)
{
	return rlbot::flat::Vector3(vec[0], vec[1], vec[2]);
}

void emplacePrediction(std::list<BallPrediction::BallSlice>* prediction) {

	std::vector<flatbuffers::Offset<rlbot::flat::PredictionSlice>> slices;

	flatbuffers::FlatBufferBuilder builder;

	for (std::list<BallPrediction::BallSlice>::iterator it = prediction->begin(); it != prediction->end(); it++) {

		rlbot::flat::PhysicsBuilder physicsBuilder(builder);
		physicsBuilder.add_location(&convertVec(it->Location));
		physicsBuilder.add_velocity(&convertVec(it->Velocity));
		physicsBuilder.add_angularVelocity(&convertVec(it->AngularVelocity));

		auto physOffset = physicsBuilder.Finish();

		rlbot::flat::PredictionSliceBuilder sliceBuilder(builder);
		sliceBuilder.add_gameSeconds(it->gameSeconds);
		sliceBuilder.add_physics(physOffset);
		slices.push_back(sliceBuilder.Finish());
	}

	auto slicesOffset = builder.CreateVector(slices);

	rlbot::flat::BallPredictionBuilder predictionBuilder(builder);
	predictionBuilder.add_slices(slicesOffset);

	builder.Finish(predictionBuilder.Finish());

	static BoostUtilities::SharedMemWriter ballPredictionWriter(BoostConstants::BallPredictionName);

	ballPredictionWriter.writeData(builder.GetBufferPointer(), builder.GetSize());
}


int runBallPrediction()
{
	printf("Ball Prediction Service Started\n");

	BallPrediction::PredictionService predictionService(6.0, 1.0 / 60);

	std::list<BallPrediction::BallSlice> empty;
	emplacePrediction(&empty); // Clear out any previous predictions

	while (true) 
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(16));

		ByteBuffer buf = GameFunctions::UpdateLiveDataPacketFlatbuffer();

		if (buf.size < 4) {
			continue; // Don't attempt to deserialize a packet if it's really small.
		}

		auto packet = flatbuffers::GetRoot<rlbot::flat::GameTickPacket>(buf.ptr);

		auto ball = packet->ball();

		if (ball != nullptr) {

			auto ballPhys = ball->physics();

			BallPrediction::BallSlice slice;
			slice.Location = convertVec(ballPhys->location());
			slice.Velocity = convertVec(ballPhys->velocity());
			slice.AngularVelocity = convertVec(ballPhys->angularVelocity());
			slice.gameSeconds = packet->gameInfo()->secondsElapsed();


			std::list<BallPrediction::BallSlice>* prediction = predictionService.updatePrediction(slice);

			emplacePrediction(prediction);
		}

		delete buf.ptr;
	}
	
	printf("Ball Prediction Service Exiting\n");
	return 0;
}

void signalHandler(int signum) {
	exit(signum);
}


int main()
{
	try
	{
		signal(SIGINT, signalHandler);
		signal(SIGABRT, signalHandler); 
		runBallPrediction();
	}
	catch (std::exception e)
	{
		printf("Encountered a std exception: %s \n", e.what());
	}
	catch (...)
	{
		printf("Encountered some kind of exception!\n");
	}
}