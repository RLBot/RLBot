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
