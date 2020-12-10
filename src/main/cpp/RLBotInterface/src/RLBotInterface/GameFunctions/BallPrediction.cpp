#include <DebugHelper.hpp>
#include <Messages.hpp>

#include "BallPrediction.hpp"
#include <MessageTranslation/FlatbufferTranslator.hpp>
#include <MutexUtilities/SafeFlatbufferHolder.hpp>
#include <rlbot_generated.h>
#include "GameFunctions/GameFunctions.hpp"

namespace BallPrediction
{

	static SafeFlatbufferHolder ball_prediction_flatbuffer;

	void setBallPredictionFlatbuffer(std::string flatbuffer_content) {
		ball_prediction_flatbuffer.set(flatbuffer_content);
	}

	std::deque<Slice> getTrimmedSliceList(ByteBuffer flatbuffer) 
	{
		auto slice_list = FlatbufferTranslator::translateToBallSliceVector(flatbuffer);

		// Get time from latest packet
		ByteBuffer packet_data = GameFunctions::UpdateLiveDataPacketFlatbuffer();
		if (packet_data.size > 0) {
			auto packet = flatbuffers::GetRoot<rlbot::flat::GameTickPacket>(packet_data.ptr);
			float seconds_elapsed = packet->gameInfo()->secondsElapsed();

			// Remove slices that come from before the time, but never go under CONST_MAXSLICES because this can confuse bots worse.
			while (slice_list.size() > CONST_MAXSLICES && slice_list.front().gameSeconds < seconds_elapsed) {
				slice_list.pop_front();
			}

			if (slice_list.empty())
			{
				// Make sure we have at least one slice, to avoid breaking bots who are expecting one.
				Slice current;
				current.gameSeconds = packet->gameInfo()->secondsElapsed();
				FlatbufferTranslator::fillPhysicsStruct(packet->ball()->physics(), &current.physics);
				slice_list.push_back(current);
			}
		}
		
		while (slice_list.size() > CONST_MAXSLICES) {
			slice_list.pop_back();
		}

		return slice_list;
	}

	extern "C" ByteBuffer RLBOT_CORE_API GetBallPrediction()
	{
		ByteBuffer flatbuffer = ball_prediction_flatbuffer.copyOut();
		auto slice_list = getTrimmedSliceList(flatbuffer);
		delete[] flatbuffer.ptr;

		std::vector<flatbuffers::Offset<rlbot::flat::PredictionSlice>> slices;

		flatbuffers::FlatBufferBuilder builder;

		for (Slice slice: slice_list) {

			auto location = rlbot::flat::Vector3(slice.physics.location.x, slice.physics.location.y, slice.physics.location.z);
			auto velocity = rlbot::flat::Vector3(slice.physics.velocity.x, slice.physics.velocity.y, slice.physics.velocity.z);
			auto angularVelocity = rlbot::flat::Vector3(slice.physics.angularVelocity.x, slice.physics.angularVelocity.y, slice.physics.angularVelocity.z);

			rlbot::flat::PhysicsBuilder physicsBuilder(builder);
			physicsBuilder.add_location(&location);
			physicsBuilder.add_velocity(&velocity);
			physicsBuilder.add_angularVelocity(&angularVelocity);

			auto physOffset = physicsBuilder.Finish();

			rlbot::flat::PredictionSliceBuilder sliceBuilder(builder);
			sliceBuilder.add_gameSeconds(slice.gameSeconds);
			sliceBuilder.add_physics(physOffset);
			slices.push_back(sliceBuilder.Finish());
		}

		auto slicesOffset = builder.CreateVector(slices);

		rlbot::flat::BallPredictionBuilder predictionBuilder(builder);
		predictionBuilder.add_slices(slicesOffset);

		builder.Finish(predictionBuilder.Finish());

		unsigned char *buffer = new unsigned char[builder.GetSize()];
		memcpy(buffer, builder.GetBufferPointer(), builder.GetSize());

		ByteBuffer buf;
		buf.ptr = buffer;
		buf.size = builder.GetSize();
		return buf;
	}

	// Ctypes
	extern "C" RLBotCoreStatus RLBOT_CORE_API GetBallPredictionStruct(BallPredictionPacket* pBallPrediction)
	{
		ByteBuffer flatbuffer = ball_prediction_flatbuffer.copyOut();
		auto slice_list = getTrimmedSliceList(flatbuffer);
		delete[] flatbuffer.ptr;
		
		int i = 0;
		for (Slice slice : slice_list) {
			if (i < CONST_MAXSLICES) {
				pBallPrediction->slice[i++] = slice;
			}
		}
		pBallPrediction->numSlices = std::min(CONST_MAXSLICES, (int)slice_list.size());

		return RLBotCoreStatus::Success;
	}
}