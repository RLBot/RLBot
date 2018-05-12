// A list of constants used by boost
// Typically each boost queue has a shared memory and a mutex
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
