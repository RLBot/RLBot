#ifndef MATCHDATAPACKET_HPP
#define MATCHDATAPACKET_HPP

#include "LiveDataPacket.hpp"

struct GoalInfo
{
	unsigned char           teamNum;
	PyStruct::Vector3       location;
	PyStruct::Vector3       direction;
	float					width;
	float					height;
};

struct BoostPad
{
	PyStruct::Vector3       location;
	bool                    fullBoost;
};

struct FieldInfo
{
	BoostPad                boostPads[CONST_MaxBoosts];
	int                     numBoosts;
	GoalInfo                goals[CONST_MaxGoals];
	int                     numGoals;
};

#endif