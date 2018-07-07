#ifndef PACKETSTRUCTS_HPP
#define PACKETSTRUCTS_HPP

#define CONST_MAX_MESSAGE_SIZE						0x1000

#define CONST_GAME_INPUT_SIZE						0x10000
#define CONST_RENDER_INPUT_SIZE						0x50000
#define CONST_CALLBACK_INPUT_SIZE					0x10000

#include "LiveDataPacket.hpp"
#include "MatchDataPacket.hpp"
#include "MatchSettings.hpp"

#include "..\MessageStructs\Message.hpp"

struct PlayerInput
{
	float					Throttle;
	float					Steer;
	float					Pitch;
	float					Yaw;
	float					Roll;
	bool					Jump;
	bool					Boost;
	bool					Handbrake;
};

struct IndexedPlayerInput
{
	int Index;
	PlayerInput PlayerInput;
};

#endif