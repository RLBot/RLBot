#include <thread>
#include <GameFunctions/GameFunctions.hpp>
#include <Interface.hpp>

int main()
{
	while (!Interface::IsInitialized())
		std::this_thread::sleep_for(std::chrono::microseconds(100));

	MatchSettings settings {0};

	PlayerConfiguration& player1 = settings.playerConfiguration[0];
	player1.bot = true;
	player1.rlbotControlled = true;

	PlayerConfiguration& player2 = settings.playerConfiguration[1];
	player2.bot = true;
	player2.rlbotControlled = true;

	settings.numPlayers = 2;
	settings.gameMode = GameMode::Soccer;
	settings.gameMap = GameMap::Mannfield;
	settings.skipReplays = false;
	settings.instantStart = false;
	
	MutatorSettings& mutators = settings.mutatorSettings;
	mutators.matchLength = MatchLength::Unlimited;
	mutators.maxScore = MaxScore::Unlimited;
	mutators.overtimeOptions = OvertimeOption::Unlimited;
	mutators.seriesLengthOptions = SeriesLengthOption::Unlimited;
	mutators.gameSpeedOptions = GameSpeedOption::Default;
	mutators.ballMaxSpeedOptions = BallMaxSpeedOption::Default;
	mutators.ballTypeOptions = BallTypeOption::Default;
	mutators.ballWeightOptions = BallWeightOption::Default;
	mutators.ballSizeOptions = BallSizeOption::Default;
	mutators.ballBouncinessOptions = BallBouncinessOption::Default;
	mutators.boostOptions = BoostOption::Normal_Boost;
	mutators.rumbleOptions = RumbleOption::None;
	mutators.boostStrengthOptions = BoostStrengthOption::One;
	mutators.gravityOptions = GravityOption::Default;
	mutators.demolishOptions = DemolishOption::Default;
	mutators.respawnTimeOptions = RespawnTimeOption::Three_Seconds;

	GameFunctions::StartMatch(settings);

	return 0;
}