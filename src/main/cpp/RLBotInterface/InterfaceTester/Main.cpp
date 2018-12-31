#include <Windows.h>
#include <GameFunctions\GameFunctions.hpp>
#include <Interface.hpp>

int main()
{
	while (!Interface::IsInitialized())
		Sleep(100);

	MatchSettings settings;
	ZeroMemory(&settings, sizeof(MatchSettings));

	PlayerConfiguration& player1 = settings.PlayerConfiguration[0];
	player1.Bot = false;
	player1.RLBotControlled = false;

	settings.NumPlayers = 1;
	settings.GameMode = GameMode::Soccer;
	settings.GameMap = GameMap::Mannfield;
	settings.SkipReplays = false;
	settings.InstantStart = false;
	
	MutatorSettings& mutators = settings.MutatorSettings;
	mutators.MatchLength = MatchLength::Five_Minutes;
	mutators.MaxScore = MaxScore::Unlimited;
	mutators.OvertimeOptions = OvertimeOption::Unlimited;
	mutators.SeriesLengthOptions = SeriesLengthOption::Unlimited;
	mutators.GameSpeedOptions = GameSpeedOption::Default;
	mutators.BallMaxSpeedOptions = BallMaxSpeedOption::Default;
	mutators.BallTypeOptions = BallTypeOption::Default;
	mutators.BallWeightOptions = BallWeightOption::Default;
	mutators.BallSizeOptions = BallSizeOption::Default;
	mutators.BallBouncinessOptions = BallBouncinessOption::Default;
	mutators.BoostOptions = BoostOption::Normal_Boost;
	mutators.RumbleOptions = RumbleOption::None;
	mutators.BoostStrengthOptions = BoostStrengthOption::One;
	mutators.GravityOptions = GravityOption::Default;
	mutators.DemolishOptions = DemolishOption::Default;
	mutators.RespawnTimeOptions = RespawnTimeOption::Three_Seconds;

	GameFunctions::StartMatch(settings, nullptr, nullptr);

	return ERROR_SUCCESS;
}