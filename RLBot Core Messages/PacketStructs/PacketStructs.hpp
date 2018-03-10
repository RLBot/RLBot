#ifndef PACKETSTRUCTS_HPP
#define PACKETSTRUCTS_HPP

#include <SDK.hpp>

#include "MatchSettingsStructs.hpp"
#include "MatchStructs.hpp"
#include "LiveDataStructs.hpp"

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

struct GameOutputData
{
	LiveDataWrapper			LiveData;
	MatchDataWrapper		MatchData;
	CallbackOutput			CallbackOutput;
};

#endif