#ifndef RAWPHYSICSSTRUCTS_HPP
#define RAWPHYSICSSTRUCTS_HPP

#include "LiveDataPacket.hpp"
#include "PacketStructs.hpp"

struct Quaternion
{
	float X;
	float Y;
	float Z;
	float W;
};

struct RigidBodyState
{
	int						Frame;
	PyStruct::Vector3 		Location;
	Quaternion 				Rotation;
	PyStruct::Vector3		Velocity;
	PyStruct::Vector3		AngularVelocity;
};

struct PlayerRigidBodyState
{
	RigidBodyState			State;
	PlayerInput				Input;
};

struct BallRigidBodyState
{
	RigidBodyState			State;
};

struct RigidBodyTick
{
	BallRigidBodyState		Ball;
	PlayerRigidBodyState	Players[CONST_MaxPlayers];
	int						NumPlayers;
};


#endif