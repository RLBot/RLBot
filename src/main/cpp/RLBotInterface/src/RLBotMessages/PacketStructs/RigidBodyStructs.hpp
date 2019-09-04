#ifndef RAWPHYSICSSTRUCTS_HPP
#define RAWPHYSICSSTRUCTS_HPP

#include "LiveDataPacket.hpp"
#include "PacketStructs.hpp"

struct Quaternion
{
	float x;
	float y;
	float z;
	float w;
};

struct RigidBodyState
{
	int						frame;
	PyStruct::Vector3 		location;
	Quaternion 				rotation;
	PyStruct::Vector3		velocity;
	PyStruct::Vector3		angularVelocity;
};

struct PlayerRigidBodyState
{
	RigidBodyState			state;
	PlayerInput				input;
};

struct BallRigidBodyState
{
	RigidBodyState			state;
};

struct RigidBodyTick
{
	BallRigidBodyState		ball;
	PlayerRigidBodyState	players[CONST_MaxPlayers];
	int						numPlayers;
};


#endif