#ifndef MATCHDATAPACKET_HPP
#define MATCHDATAPACKET_HPP

struct GoalInfo
{
	PyStruct::Vector3		Location;
	PyStruct::Rotator		Rotation;
	PyStruct::Vector3		Direction;
	PyStruct::Vector3		LocalMin;
	PyStruct::Vector3		LocalMax;
	PyStruct::Vector3		LocalExtent;
	unsigned char			TeamNum;
};

struct FieldInfo
{
	PyStruct::Rotator		FieldOrientation;
	PyStruct::Vector3		FieldSize;
	PyStruct::Vector3		FieldExtent;
	PyStruct::Vector3		FieldCenter;
	float					GroundZ;
	GoalInfo				Goals[2];
};

#endif