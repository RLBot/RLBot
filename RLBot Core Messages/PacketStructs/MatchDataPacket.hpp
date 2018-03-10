#ifndef MATCHDATAPACKET_HPP
#define MATCHDATAPACKET_HPP

#include <SDK.hpp>

struct GoalInfo
{
	Vector3					Location;
	Rotator					Rotation;
	Vector3					Direction;
	Vector3					LocalMin;
	Vector3					LocalMax;
	Vector3					LocalExtent;
	unsigned char			TeamNum;
};

struct FieldInfo
{
	Rotator					FieldOrientation;
	Vector3					FieldSize;
	Vector3					FieldExtent;
	Vector3					FieldCenter;
	float					GroundZ;
	GoalInfo				Goals[2];
};

struct MatchDataPacket
{
	FieldInfo				FieldInfo;
};

struct MatchDataWrapper
{
	long					ExchangedValue;
	MatchDataPacket			MatchDataPacket;
};

#endif