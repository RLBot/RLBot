#pragma once

#include "..\PacketStructs\LiveDataPacket.hpp"
#include "..\PacketStructs\PacketStructs.hpp"
#include "..\MessageStructs\ByteBuffer.hpp"
#include <flatbuffers\flatbuffers.h>

namespace FlatbufferTranslator {

	void translateToStruct(ByteBuffer flatbufferData, LiveDataPacket* packet);

	void translateToPrediction(ByteBuffer flatbufferData, BallPredictionPacket* packet);

	void translateToFieldInfoStruct(ByteBuffer flatbufferData, FieldInfo* packet);

	void inputStructToFlatbuffer(flatbuffers::FlatBufferBuilder* builder, const PlayerInput& playerInput, int playerIndex);
}