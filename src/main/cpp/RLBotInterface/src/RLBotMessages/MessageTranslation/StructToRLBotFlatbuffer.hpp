#ifndef GAMEDATAFLATREADER_HPP
#define GAMEDATAFLATREADER_HPP

#include <flatbuffers/flatbuffers.h>
#include "PacketStructs/LiveDataPacket.hpp"
#include "PacketStructs/MatchDataPacket.hpp"
#include "PacketStructs/MatchSettings.hpp"
#include "PacketStructs/RigidBodyStructs.hpp"
#include <rlbot_generated.h>

namespace StructToRLBotFlatbuffer
{
	bool FillGameDataPacket(flatbuffers::FlatBufferBuilder* builder, LiveDataPacket liveDataPacket);
	bool FillFieldInfo(flatbuffers::FlatBufferBuilder* builder, FieldInfo fieldInfo);
	bool FillRigidBody(flatbuffers::FlatBufferBuilder* builder, RigidBodyTick rigidBodyTick);
	bool BuildStartMatchMessage(flatbuffers::FlatBufferBuilder* builder, MatchSettings matchSettings);

    flatbuffers::Offset<rlbot::flat::PlayerInfo> createPlayerInfo(flatbuffers::FlatBufferBuilder* builder, PlayerInfo playerInfo);
    flatbuffers::Offset<rlbot::flat::GameInfo> createGameInfo(flatbuffers::FlatBufferBuilder* builder, GameInfo gameInfo);
    flatbuffers::Offset<rlbot::flat::BoostPadState> createBoostPadState(flatbuffers::FlatBufferBuilder* builder, BoostInfo gameBoost);
    flatbuffers::Offset<rlbot::flat::DropshotTile> createDropshotTile(flatbuffers::FlatBufferBuilder* builder, TileInfo dropshotTile);
    flatbuffers::Offset<rlbot::flat::BallInfo> createBallInfo(flatbuffers::FlatBufferBuilder* builder, BallInfo ballInfo);
}

#endif