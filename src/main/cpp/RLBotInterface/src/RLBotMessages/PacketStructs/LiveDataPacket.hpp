#ifndef LIVEDATAPACKET_HPP
#define LIVEDATAPACKET_HPP


#define CONST_MaxBoosts		50
#define CONST_MaxTiles		200
#define CONST_MaxTeams		2
#define CONST_MaxGoals		200
#define CONST_MaxPlayers	64
#define CONST_MAXSLICES		360

struct ScoreInfo
{
	int 					score;
	int 					goals;
	int 					ownGoals;
	int 					assists;
	int 					saves;
	int 					shots;
	int 					demolitions;
};

namespace PyStruct 
{
	struct Vector3
	{
		float x;
		float y;
		float z;
	};

	struct Rotator
	{
		float pitch;
		float yaw;
		float roll;
	};

	struct Color
	{
		unsigned char b;
		unsigned char g;
		unsigned char r;
		unsigned char a;
	};
}

struct BoxShape
{
	float length;
	float width;
	float height;
};

struct SphereShape {
	float diameter;
};

struct CylinderShape {
	float diameter;
	float height;
};

enum CollisionShapeType { BoxType, SphereType, CylinderType };

struct CollisionShape {
	CollisionShapeType type;
	BoxShape box;
	SphereShape sphere;
	CylinderShape cylinder;
};

struct Physics
{
	PyStruct::Vector3 		location;
	PyStruct::Rotator 		rotation;
	PyStruct::Vector3		velocity;
	PyStruct::Vector3		angularVelocity;
};

struct PlayerInfo
{
	Physics 				physics;
	ScoreInfo 				score;
	bool					demolished;
	bool					onGround;
	bool 					superSonic;
	bool 					bot;
	bool					jumped;
	bool					doubleJumped;
	wchar_t					name[32];
	unsigned char			team;
	int 					boost;
	BoxShape				hitbox;
	PyStruct::Vector3		hitboxOffset;
	int						spawnId;
};

struct BoostInfo
{
	bool 					active;
	float 					timer;
};

struct TileInfo
{
	int						tileState;
};

struct TeamInfo
{
	int						teamIndex;
	int						score;
};

struct Touch
{
	wchar_t					playerName[32];
	float					timeSeconds;
	PyStruct::Vector3		hitLocation;
	PyStruct::Vector3		hitNormal;
	int						team;
	int						playerIndex;
};

struct DropShotBallInfo
{
	float					absorbedForce;
	int						damageIndex;
	float					forceAccumRecent;
};

struct Slice
{
	Physics 				physics;
	float					gameSeconds;
};

struct BallPredictionPacket
{
	Slice				slice[CONST_MAXSLICES];
	int					numSlices;
};

struct BallInfo
{
	Physics 				physics;
	Touch					latestTouch;
	DropShotBallInfo		dropShotInfo;
	CollisionShape			collisionShape;
};

struct GameInfo
{
	float					timeSeconds;
	float					gameTimeRemaining;
	bool					overTime;
	bool					unlimitedTime;
	bool					roundActive;
	bool					kickoffPause;
	bool					matchEnded;
	float					worldGravityZ;
	float					gameSpeed;
	int						frameNum;
};

struct LiveDataPacket
{
	PlayerInfo 				gameCars[CONST_MaxPlayers];
	int						numCars;
	BoostInfo 				gameBoosts[CONST_MaxBoosts];
	int						numBoosts;
	BallInfo  				gameBall;
	GameInfo				gameInfo;
	TileInfo				gameTiles[CONST_MaxTiles];
	int						numTiles;
	TeamInfo				teams[CONST_MaxTeams];
	int						numTeams;
};

#endif