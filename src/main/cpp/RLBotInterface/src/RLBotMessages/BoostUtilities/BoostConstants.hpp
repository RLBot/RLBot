#ifndef BOOSTCONSTANTS_HPP
#define BOOSTCONSTANTS_HPP

namespace BoostConstants
{
	// Game Data
	extern const char* GameDataFlatName;

	// Game Data
	extern const char* PhysicsTickFlatName;

	// Player Input
	extern const char* PlayerInputFlatQueueName;

	// Field information
	extern const char* FieldInfoFlatName;

	// Rendering
	extern const char* RenderingFlatQueueName;

	// Chat
	extern const char* QuickChatFlatQueueName;

	// Chat messages distribution
	extern const char* QuickChatDistributionName;

	// Game State Setting
	extern const char* GameStateFlatQueueName;

	// Ball prediction
	extern const char* BallPredictionName;

	// Match control
	extern const char* MatchControlQueueName;

	// Reading the match settings back out
	extern const char* MatchSettingsName;

	// Location to store the number of frames processed by RLBot
	extern const char* FrameCountName;

	std::string buildSharedMemName(const char* baseName);
	std::string buildMutexName(const char* baseName);
};

#endif
