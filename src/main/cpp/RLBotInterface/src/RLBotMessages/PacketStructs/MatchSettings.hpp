#ifndef MATCHSETTINGS_STRUCTS_HPP
#define MATCHSETTINGS_STRUCTS_HPP

#include "LiveDataPacket.hpp"
#include "PacketStructs/Color.hpp"

struct PlayerConfiguration
{
	bool					bot;
	bool					rlbotControlled;
	float					botSkill;
	int						humanIndex;
	wchar_t					name[32];
	unsigned char			team;
	unsigned char			teamColorID;
	unsigned char			customColorID;
	int						carID;
	int						decalID;
	int						wheelsID;
	int						boostID;
	int						antennaID;
	int						hatID;
	int						paintFinishID;
	int						customFinishID;
	int						engineAudioID;
	int						trailsID;
	int						goalExplosionID;
	int						carPaintID;
	int						decalPaintID;
	int						wheelsPaintID;
	int						boostPaintID;
	int						antennaPaintID;
	int						hatPaintID;
	int						trailsPaintID;
	int						goalExplosionPaintID;
	bool					useRgbLookup;
	Color					primaryColorLookup;
	Color					secondaryColorLookup;
	int						spawnId;
};

enum GameMode
{
	Soccer,
	Hoops,
	Dropshot,
	Hockey,
	Rumble
};

enum GameMap
{
	DFHStadium,
	Mannfield,
	ChampionsField,
	UrbanCentral,
	BeckwithPark,
	UtopiaColiseum,
	Wasteland,
	NeoTokyo,
	AquaDome,
	StarbaseArc,
	Farmstead,
	SaltyShores,
	DFHStadium_Stormy,
	DFHStadium_Day,
	Mannfield_Stormy,
	Mannfield_Night,
	ChampionsField_Day,
	BeckwithPark_Stormy,
	BeckwithPark_Midnight,
	UrbanCentral_Night,
	UrbanCentral_Dawn,
	UtopiaColiseum_Dusk,
	DFHStadium_Snowy,
	Mannfield_Snowy,
	UtopiaColiseum_Snowy,
	Badlands,
	Badlands_Night,
	TokyoUnderpass,
	Arctagon,
	Pillars,
	Cosmic,
	DoubleGoal,
	Octagon,
	Underpass,
	UtopiaRetro,
	Hoops_DunkHouse,
	DropShot_Core707,
	ThrowbackStadium,
	ForbiddenTemple,
	RivalsArena,
	Farmstead_Night,
	SaltyShores_Night
};

enum class MatchLength
{
	Five_Minutes,
	Ten_Minutes,
	Twenty_Minutes,
	Unlimited
};

enum class MaxScore
{
	Unlimited,
	One_Goal,
	Three_Goals,
	Five_Goals
};

enum class OvertimeOption
{
	Unlimited,
	Five_Max_First_Score,
	Five_Max_Random_Team
};

enum class SeriesLengthOption
{
	Unlimited,
	Three_Games,
	Five_Games,
	Seven_Games
};

enum class GameSpeedOption
{
	Default,
	Slo_Mo,
	Time_Warp
};

enum class BallMaxSpeedOption
{
	Default,
	Slow,
	Fast,
	Super_Fast
};

enum class BallTypeOption
{
	Default,
	Cube,
	Puck,
	Basketball
};

enum class BallWeightOption
{
	Default,
	Light,
	Heavy,
	Super_Light
};

enum class BallSizeOption
{
	Default,
	Small,
	Large,
	Gigantic
};

enum class BallBouncinessOption
{
	Default,
	Low,
	High,
	Super_High
};

enum class BoostOption
{
	Normal_Boost,
	Unlimited_Boost,
	Slow_Recharge,
	Rapid_Recharge,
	No_Boost
};

enum class RumbleOption
{
	None,
	Default,
	Slow,
	Civilized,
	Destruction_Derby,
	Spring_Loaded,
	Spikes_Only,
	Spike_Rush
};

enum class BoostStrengthOption
{
	One,
	OneAndAHalf,
	Two,
	Ten
};

enum class GravityOption
{
	Default,
	Low,
	High,
	Super_High
};

enum class DemolishOption
{
	Default,
	Disabled,
	Friendly_Fire,
	On_Contact,
	On_Contact_FF
};

enum class RespawnTimeOption
{
	Three_Seconds,
	Two_Seconds,
	One_Seconds,
	Disable_Goal_Reset
};

struct MutatorSettings
{
	MatchLength				matchLength;
	MaxScore				maxScore;
	OvertimeOption			overtimeOptions;
	SeriesLengthOption		seriesLengthOptions;
	GameSpeedOption			gameSpeedOptions;
	BallMaxSpeedOption		ballMaxSpeedOptions;
	BallTypeOption			ballTypeOptions;
	BallWeightOption		ballWeightOptions;
	BallSizeOption			ballSizeOptions;
	BallBouncinessOption	ballBouncinessOptions;
	BoostOption				boostOptions;
	RumbleOption			rumbleOptions;
	BoostStrengthOption		boostStrengthOptions;
	GravityOption			gravityOptions;
	DemolishOption			demolishOptions;
	RespawnTimeOption		respawnTimeOptions;
};

enum ExistingMatchBehavior
{
	Restart_If_Different,
	Restart,
	Continue_And_Spawn
};

struct MatchSettings
{
	PlayerConfiguration		playerConfiguration[CONST_MaxPlayers];
	int						numPlayers;
	GameMode				gameMode;
	GameMap					gameMap;
	bool					skipReplays;
	bool					instantStart;
	MutatorSettings			mutatorSettings;
	ExistingMatchBehavior	existingMatchBehavior;
	bool					enableLockstep;
};

#endif
