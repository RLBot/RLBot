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

enum Map
{
	Map_AquaDome,
	Map_BeckwithPark,
	Map_ChampionsField,
	Map_DFH,
	Map_Manfield,
	Map_NeoTokyo,
	Map_Starbase,
	Map_UrbanCentral,
	Map_UtopiaColiseum,
	Map_Waseland
};

struct MatchSettings
{

};

#endif