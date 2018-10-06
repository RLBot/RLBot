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

	// Game State Setting
	extern const char* GameStateFlatQueueName;

	// Ball prediction
	extern const char* BallPredictionName;

	std::string buildSharedMemName(const char* baseName);
	std::string buildMutexName(const char* baseName);
};

#endif
