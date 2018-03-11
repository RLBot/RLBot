#ifndef PROTO_CONVERSIONS_HPP
#define PROTO_CONVERSIONS_HPP

#include <game_data.pb.h>
#include <PacketStructs\LiveDataPacket.hpp>

namespace ProtoConversions {
	rlbot::api::GameTickPacket* convert(LiveDataPacket* pLiveData);
}

#endif // !PROTO_CONVERSIONS_HPP
