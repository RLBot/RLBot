#ifndef PACKETSTRUCTS_HPP
#define PACKETSTRUCTS_HPP

#include <SDK.hpp>

#include "MatchSettingsStructs.hpp"
#include "MatchStructs.hpp"

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

struct PlayerInfo
{
	Vector3 				Location;
	Rotator 				Rotation;
	Vector3					Velocity;
	Vector3					AngularVelocity;
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
	Vector3 				Location;
	bool 					Active;
	float 					Timer;
};

struct Touch
{
	wchar_t					PlayerName[32];
	float					TimeSeconds;
	Vector3					HitLocation;
	Vector3					HitNormal;
};

struct BallInfo
{
	Vector3 				Location;
	Rotator 				Rotation;
	Vector3 				Velocity;
	Vector3 				AngularVelocity;
	Vector3 				Acceleration;
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

struct PlayerInput
{
	float					Throttle;
	float					Steer;
	float					Pitch;
	float					Yaw;
	float					Roll;
	bool					Jump;
	bool					Boost;
	bool					Handbrake;
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

struct GameInput
{
	long					ExchangedValue;
	unsigned char			Data[0x5000];
	unsigned long			NumMessages;
};

struct RenderInput
{
	long					ExchangedValue;
	unsigned char			Data[0x50000];
	unsigned long			NumMessages;
};

struct CallbackOutput
{
	long					ExchangedValue;
	unsigned char			Data[0x5000];
	unsigned long			NumMessages;
};

struct GameInputData
{
	GameInput				GameInput;
	RenderInput				RenderInput;
};

struct LiveDataWrapper
{
	long					ExchangedValue;
	LiveDataPacket			LiveDataPacket;
};

struct GameOutputData
{
	LiveDataWrapper			LiveData;
	MatchDataWrapper		MatchData;
	CallbackOutput			CallbackOutput;
};

#endif