#ifndef PACKETSTRUCTS_HPP
#define PACKETSTRUCTS_HPP

#include "LiveDataPacket.hpp"
#include "MatchDataPacket.hpp"
#include "MatchSettings.hpp"

struct PlayerInput
{
	float					throttle;
	float					steer;
	float					pitch;
	float					yaw;
	float					roll;
	bool					jump;
	bool					boost;
	bool					handbrake;
	bool					useItem;
};

struct IndexedPlayerInput
{
	int index;
	PlayerInput playerInput;
};

#endif