#include "ProtoConversions.hpp"

rlbot::api::GameTickPacket* convert(LiveDataPacket* pLiveData) {
	GameTickPacket gameTickPacket = GameTickPacket();
	return &gameTickPacket;
}
