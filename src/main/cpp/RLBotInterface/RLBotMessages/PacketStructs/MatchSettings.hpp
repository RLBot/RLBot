#ifndef MATCHSETTINGS_STRUCTS_HPP
#define MATCHSETTINGS_STRUCTS_HPP

struct PlayerConfiguration
{
	bool					Bot;
	bool					RLBotControlled;
	float					BotSkill;
	int						HumanIndex;
	wchar_t					Name[32];
	unsigned char			Team;
	unsigned char			TeamColorID;
	unsigned char			CustomColorID;
	int						CarID;
	int						DecalID;
	int						WheelsID;
	int						BoostID;
	int						AntennaID;
	int						HatID;
	int						PaintFinishID;
	int						CustomFinishID;
	int						EngineAudioID;
	int						TrailsID;
	int						GoalExplosionID;
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
	Workshop_Aerial_Map, // http://steamcommunity.com/sharedfiles/filedetails/?id=1212847139&searchtext=
	Workshop_BeachVolley, // http://steamcommunity.com/sharedfiles/filedetails/?id=916532343&searchtext=
	Workshop_DribblingChallenge2, // http://steamcommunity.com/sharedfiles/filedetails/?id=964271505&searchtext=
	Workshop_DribblingChallenge, // http://steamcommunity.com/sharedfiles/filedetails/?id=814218628&searchtext=
	Workshop_ObstacleCourse2, // http://steamcommunity.com/sharedfiles/filedetails/?id=828803580&searchtext=
	Workshop_ObstacleCourse, // http://steamcommunity.com/sharedfiles/filedetails/?id=814207936
	Workshop_ShipYarr // http://steamcommunity.com/sharedfiles/filedetails/?id=817314448&searchtext=
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
	Spikes_Only
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
	MatchLength				MatchLength;
	MaxScore				MaxScore;
	OvertimeOption			OvertimeOptions;
	SeriesLengthOption		SeriesLengthOptions;
	GameSpeedOption			GameSpeedOptions;
	BallMaxSpeedOption		BallMaxSpeedOptions;
	BallTypeOption			BallTypeOptions;
	BallWeightOption		BallWeightOptions;
	BallSizeOption			BallSizeOptions;
	BallBouncinessOption	BallBouncinessOptions;
	BoostOption				BoostOptions;
	RumbleOption			RumbleOptions;
	BoostStrengthOption		BoostStrengthOptions;
	GravityOption			GravityOptions;
	DemolishOption			DemolishOptions;
	RespawnTimeOption		RespawnTimeOptions;
};

struct MatchSettings
{
	PlayerConfiguration		PlayerConfiguration[CONST_MaxPlayers];
	int						NumPlayers;
	GameMode				GameMode;
	GameMap					GameMap;
	bool					SkipReplays;
	bool					InstantStart;
	MutatorSettings			MutatorSettings;
};

#endif