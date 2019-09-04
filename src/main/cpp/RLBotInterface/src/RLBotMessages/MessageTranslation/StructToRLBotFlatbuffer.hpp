#ifndef GAMEDATAFLATREADER_HPP
#define GAMEDATAFLATREADER_HPP

#include <flatbuffers/flatbuffers.h>
#include "PacketStructs/LiveDataPacket.hpp"
#include "PacketStructs/MatchDataPacket.hpp"
#include "PacketStructs/MatchSettings.hpp"
#include "PacketStructs/RigidBodyStructs.hpp"

namespace StructToRLBotFlatbuffer
{
	bool FillGameDataPacket(flatbuffers::FlatBufferBuilder* builder, LiveDataPacket liveDataPacket);
	bool FillFieldInfo(flatbuffers::FlatBufferBuilder* builder, FieldInfo fieldInfo);
	bool FillRigidBody(flatbuffers::FlatBufferBuilder* builder, RigidBodyTick rigidBodyTick);
	bool BuildStartMatchMessage(flatbuffers::FlatBufferBuilder* builder, MatchSettings matchSettings);
}

#endif