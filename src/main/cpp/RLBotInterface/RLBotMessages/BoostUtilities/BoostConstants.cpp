#include <string>

// A list of constants used by boost
// Shared Memory has a shared memory name and a mutex name
// Boost queues only have a queue name
// This specifies the IDs for those
namespace BoostConstants
{
	// Game Data
	const char* GameDataFlatName = "gameDataFlat";

	// Physics Ticks
	const char* PhysicsTickFlatName = "physicsTickFlat";

	// Player Input
	const char* PlayerInputFlatQueueName = "playerInputFlatQueue";

	// Field information
	const char* FieldInfoFlatName = "fieldInfoFlat";

	// Rendering
	const char* RenderingFlatQueueName = "RenderingFlatQueue";

	// Chat
	const char* QuickChatFlatQueueName = "quickChatQueue";

	// Game State Setting
	const char* GameStateFlatQueueName = "gameStateQueue";

	// Game Data
	const char* BallPredictionName = "ballPrediction";

	std::string buildSharedMemName(const char* baseName) {
		std::string name(baseName);
		name.append("-SharedMem");
		return name;
	}
	std::string buildMutexName(const char* baseName) {
		std::string name(baseName);
		name.append("-Mutex");
		return name;
	}
};
