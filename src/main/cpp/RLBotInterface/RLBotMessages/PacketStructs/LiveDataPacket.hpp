#ifndef LIVEDATAPACKET_HPP
#define LIVEDATAPACKET_HPP


#define CONST_MaxBoosts		50
#define CONST_MaxPlayers	10

struct ScoreInfo
{
	int 					Score;
	int 					Goals;
	int 					OwnGoals;
	int 					Assists;
	int 					Saves;
	int 					Shots;
	int 					Demolitions;
};

namespace PyStruct 
{
	struct Vector3
	{
		float X;
		float Y;
		float Z;
	};

	struct Rotator
	{
		int Pitch;
		int Yaw;
		int Roll;
	};

	struct Color
	{
		unsigned char B;
		unsigned char G;
		unsigned char R;
		unsigned char A;
	};
}

struct PlayerInfo
{
	PyStruct::Vector3 		Location;
	PyStruct::Rotator 		Rotation;
	PyStruct::Vector3		Velocity;
	PyStruct::Vector3		AngularVelocity;
	ScoreInfo 				Score;
	bool					Demolished;
	bool					OnGround;
	bool 					SuperSonic;
	bool 					Bot;
	bool					Jumped;
	bool					DoubleJumped;
	wchar_t					Name[32];
	unsigned char			Team;
	int 					Boost;
};

struct BoostInfo
{
	PyStruct::Vector3 		Location;
	bool 					Active;
	float 					Timer;
};

struct Touch
{
	wchar_t					PlayerName[32];
	float					TimeSeconds;
	PyStruct::Vector3		HitLocation;
	PyStruct::Vector3		HitNormal;
};

struct BallInfo
{
	PyStruct::Vector3 		Location;
	PyStruct::Rotator 		Rotation;
	PyStruct::Vector3 		Velocity;
	PyStruct::Vector3 		AngularVelocity;
	PyStruct::Vector3 		Acceleration;
	Touch					LatestTouch;
};

struct GameInfo
{
	float					TimeSeconds;
	float					GameTimeRemaining;
	bool					OverTime;
	bool					UnlimitedTime;
	bool					RoundActive;
	bool					BallHasBeenHit;
	bool					MatchEnded;
};

struct LiveDataPacket
{
	PlayerInfo 				GameCars[CONST_MaxPlayers];
	int						NumCars;
	BoostInfo 				GameBoosts[CONST_MaxBoosts];
	int						NumBoosts;
	BallInfo  				GameBall;
	GameInfo				GameInfo;
};

#endif