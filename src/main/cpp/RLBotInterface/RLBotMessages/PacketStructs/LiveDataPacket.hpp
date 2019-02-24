#ifndef LIVEDATAPACKET_HPP
#define LIVEDATAPACKET_HPP


#define CONST_MaxBoosts		50
#define CONST_MaxTiles		200
#define CONST_MaxTeams		2
#define CONST_MaxGoals		200
#define CONST_MaxPlayers	10
#define CONST_MAXSLICES		360

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
		float Pitch;
		float Yaw;
		float Roll;
	};

	struct Color
	{
		unsigned char B;
		unsigned char G;
		unsigned char R;
		unsigned char A;
	};
}

struct Physics
{
	PyStruct::Vector3 		Location;
	PyStruct::Rotator 		Rotation;
	PyStruct::Vector3		Velocity;
	PyStruct::Vector3		AngularVelocity;
};

struct PlayerInfo
{
	Physics 				Physics;
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
	bool 					Active;
	float 					Timer;
};

struct TileInfo
{
	int						tileState;
};

struct TeamInfo
{
	int						TeamIndex;
	int						Score;
};

struct Touch
{
	wchar_t					PlayerName[32];
	float					TimeSeconds;
	PyStruct::Vector3		HitLocation;
	PyStruct::Vector3		HitNormal;
	int						Team;
};

struct DropShotBallInfo
{
	float					AbsorbedForce;
	int						DamageIndex;
	float					ForceAccumRecent;
};

struct Slice
{
	Physics 				Physics;
	float					GameSeconds;
};

struct BallPredictionPacket
{
	Slice				Slice[CONST_MAXSLICES];
	int					NumSlices;
};

struct BallInfo
{
	Physics 				Physics;
	Touch					LatestTouch;
	DropShotBallInfo		DropShotInfo;
};

struct GameInfo
{
	float					TimeSeconds;
	float					GameTimeRemaining;
	bool					OverTime;
	bool					UnlimitedTime;
	bool					RoundActive;
	bool					KickoffPause;
	bool					MatchEnded;
	float					WorldGravityZ;
	float					GameSpeed;
};

struct LiveDataPacket
{
	PlayerInfo 				GameCars[CONST_MaxPlayers];
	int						NumCars;
	BoostInfo 				GameBoosts[CONST_MaxBoosts];
	int						NumBoosts;
	BallInfo  				GameBall;
	GameInfo				GameInfo;
	TileInfo				GameTiles[CONST_MaxTiles];
	int						NumTiles;
	TeamInfo				Teams[CONST_MaxTeams];
	int						NumTeams;
};

#endif