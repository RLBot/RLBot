#ifndef MATCHDATAPACKET_HPP
#define MATCHDATAPACKET_HPP

struct GoalInfo
{
	unsigned char           TeamNum;
	PyStruct::Vector3       Location;
	PyStruct::Vector3       Direction;
};

struct BoostPad
{
	PyStruct::Vector3       Location;
	bool                    FullBoost;
};

struct FieldInfo
{
	BoostPad                BoostPads[CONST_MaxBoosts];
	int                     NumBoosts;
	GoalInfo                Goals[CONST_MaxGoals];
	int                     NumGoals;
};

#endif