// A list of constants used by boost
// Shared Memory has a shared memory name and a mutex name
// Boost queues only have a queue name
// This specifies the IDs for those
namespace BoostConstants
{
	// Game Data
	const char* GameDataSharedMemName = "gameDataSharedMem";
	const char* GameDataMutexName = "gameDataMutex";
	const char* GameDataFlatSharedMemName = "gameDataFlatSharedMem";
	const char* GameDataFlatMutexName = "gameDataFlatMutex";

	// Player Input
	const char* PlayerInputQueueName = "playerInputQueue";
	const char* PlayerInputFlatQueueName = "playerInputFlatQueue";

	// Field information
	const char* FieldInfoSharedMemName = "fieldInfoSharedMem";
	const char* FieldInfoMutexName = "fieldInfoMutex";
	const char* FieldInfoFlatSharedMemName = "fieldInfoFlatSharedMem";
	const char* FieldInfoFlatMutexName = "fieldInfoFlatMutex";

	// Rendering
	const char* RenderingFlatSharedMemName = "RenderingFlatSharedMem";
	const char* RenderingFlatMutexName = "RenderingFlatMutex";
};
