#pragma once

#include "..\PacketStructs\LiveDataPacket.hpp"
#include "..\PacketStructs\PacketStructs.hpp"
#include "..\MessageStructs\ByteBuffer.hpp"
#include "..\PacketStructs\RigidBodyStructs.hpp"
#include <flatbuffers\flatbuffers.h>

namespace FlatbufferTranslator {

	void translateToStruct(ByteBuffer flatbufferData, LiveDataPacket* packet);

	void translateToPrediction(ByteBuffer flatbufferData, BallPredictionPacket* packet);

	void translateToFieldInfoStruct(ByteBuffer flatbufferData, FieldInfo* packet);

	void translateToRigidBodyStruct(ByteBuffer flatbufferData, RigidBodyTick* physicsTick);

	void inputStructToFlatbuffer(flatbuffers::FlatBufferBuilder* builder, const PlayerInput& playerInput, int playerIndex);
}