// BallPrediction.cpp : Defines the entry point for the console application.
//

#include <stdio.h>
#include <chrono>
#include <thread>
#include <csignal>
#include <GameFunctions\GameFunctions.hpp>
#include <GameFunctions\PlayerInfo.hpp>
#include <rlbot_generated.h>
#include <BoostUtilities\BoostUtilities.hpp>
#include <BoostUtilities\BoostConstants.hpp>


int runBot()
{

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

			flatbuffers::FlatBufferBuilder builder;

			float steer = ballPhys->location()->x() > 0 ? 1.0 : -1.0;
			int playerIndex = 0; // TODO: use a real player index

			auto controls = rlbot::flat::CreateControllerState(
				builder,
				1.0,
				steer,
				1.0,
				1.0,
				1.0,
				false,
				false,
				false);

			auto input = rlbot::flat::CreatePlayerInput(builder, playerIndex, controls);

			builder.Finish(input);

			GameFunctions::UpdatePlayerInputFlatbuffer(builder.GetBufferPointer(), builder.GetSize());
		}

		delete buf.ptr;
	}

	printf("Bot Exiting\n");
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
		runBot();
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