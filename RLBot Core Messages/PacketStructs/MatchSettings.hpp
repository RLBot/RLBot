#ifndef MATCHSETTINGS_STRUCTS_HPP
#define MATCHSETTINGS_STRUCTS_HPP

#include <SDK.hpp>

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
	GameMode_DropShot,
	GameMode_Hoops,
	GameMode_Hockey,
	GameMode_Normal
};

enum MapSelection
{
	NormalMap_AquaDome,
	NormalMap_BeckwithPark,
	NormalMap_ChampionsField,
	NormalMap_DFH,
	NormalMap_Manfield,
	NormalMap_NeoTokyo,
	NormalMap_Starbase,
	NormalMap_UrbanCentral,
	NormalMap_UtopiaColiseum,
	NormalMap_Waseland,
	NormalMap_Farmstead,
	RemovedMap_ARCtagon,
	RemovedMap_Badlands,
	RemovedMap_TokyoUnderpass,
	Hoops_DunkHouse,
	DropShot_Core707,
	RocketLab_Cosmic,
	RocketLab_DoubleGoal,
	RocketLab_Octagon,
	RocketLab_Pillars,
	RocketLab_Underpass,
	RocketLab_UtopiaRetro,
	Workshop_Aerial_Map, // http://steamcommunity.com/sharedfiles/filedetails/?id=1212847139&searchtext=
	Workshop_BeachVolley, // http://steamcommunity.com/sharedfiles/filedetails/?id=916532343&searchtext=
	Workshop_DribblingChallenge2, // http://steamcommunity.com/sharedfiles/filedetails/?id=964271505&searchtext=
	Workshop_DribblingChallenge, // http://steamcommunity.com/sharedfiles/filedetails/?id=814218628&searchtext=
	Workshop_ObstacleCourse2, // http://steamcommunity.com/sharedfiles/filedetails/?id=828803580&searchtext=
	Workshop_ObstacleCourse, // http://steamcommunity.com/sharedfiles/filedetails/?id=814207936
	Workshop_ShipYarr // http://steamcommunity.com/sharedfiles/filedetails/?id=817314448&searchtext=
};

enum MapVariation
{
	Variation_Night,
	Variation_Day,
	Variation_Snowy,
	Variation_Stormy,
	Variation_Dusk
};


struct MatchSettings
{
	GameMode GameMode;
	MapSelection GameMap;
	MapVariation MapVariation;
	bool skipReplays;
	bool instantStart;
};


struct Mutators
{

};

#endif