#ifndef PROTO_CONVERSIONS_HPP
#define PROTO_CONVERSIONS_HPP

#include <game_data.pb.h>
#include <PacketStructs\LiveDataPacket.hpp>
#include <PacketStructs\PacketStructs.hpp>
#include <ErrorCodes\ErrorCodes.hpp>

typedef void* CompiledGameTickPacket;
typedef void* CompiledControllerState;

namespace ProtoConversions {
	rlbot::api::GameTickPacket* convert(LiveDataPacket* pLiveData);
	RLBotCoreStatus convert(rlbot::api::GameTickPacket* protoResult, LiveDataPacket* pLiveData);
	PlayerInput* convert(rlbot::api::ControllerState* protoResult);
}

#endif // !PROTO_CONVERSIONS_HPP
