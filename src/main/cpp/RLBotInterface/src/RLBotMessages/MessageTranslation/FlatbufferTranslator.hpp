#pragma once

#include "PacketStructs/LiveDataPacket.hpp"
#include "PacketStructs/PacketStructs.hpp"
#include "MessageStructs/ByteBuffer.hpp"
#include "PacketStructs/RigidBodyStructs.hpp"
#include <flatbuffers/flatbuffers.h>
#include <deque>
#include <rlbot_generated.h>

namespace FlatbufferTranslator {

	void translateToStruct(ByteBuffer flatbufferData, LiveDataPacket* packet);

	void translateToPrediction(ByteBuffer flatbufferData, BallPredictionPacket* packet);
	std::deque<Slice> translateToBallSliceVector(ByteBuffer flatbufferData);

	void translateToFieldInfoStruct(ByteBuffer flatbufferData, FieldInfo* packet);

	void translateToRigidBodyStruct(ByteBuffer flatbufferData, RigidBodyTick* physicsTick);

	void inputStructToFlatbuffer(flatbuffers::FlatBufferBuilder* builder, const PlayerInput& playerInput, int playerIndex);

	void inputStructFromFlatbuffer(void* flatbuffer, PlayerInput& playerInput);

	void translateToMatchSettingsStruct(ByteBuffer flatbufferData, MatchSettings* matchSettings);

	void fillPhysicsStruct(const::rlbot::flat::Physics* physics, Physics* structPhysics);
}