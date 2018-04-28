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
	Workshop_Aerial_Map, // http://steamcommunity.com/sharedfiles/filedetails/?id=1212847139&searchtext=
	Workshop_BeachVolley, // http://steamcommunity.com/sharedfiles/filedetails/?id=916532343&searchtext=
	Workshop_DribblingChallenge2, // http://steamcommunity.com/sharedfiles/filedetails/?id=964271505&searchtext=
	Workshop_DribblingChallenge, // http://steamcommunity.com/sharedfiles/filedetails/?id=814218628&searchtext=
	Workshop_ObstacleCourse2, // http://steamcommunity.com/sharedfiles/filedetails/?id=828803580&searchtext=
	Workshop_ObstacleCourse, // http://steamcommunity.com/sharedfiles/filedetails/?id=814207936
	Workshop_ShipYarr // http://steamcommunity.com/sharedfiles/filedetails/?id=817314448&searchtext=
};

enum MatchLength
{
	Five_Minutes,
	Ten_Minutes,
	Twenty_Minutes,
	Unlimited
};

enum BoostOption
{
	Normal_Boost,
	Unlimited_Boost,
	Slow_Recharge,
	Rapid_Recharge,
	No_Boost
};

struct MutatorSettings
{
	MatchLength				MatchLength;
	BoostOption				BoostOptions;
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