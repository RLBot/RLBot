#ifndef BOOSTCONSTANTS_HPP
#define BOOSTCONSTANTS_HPP

#define PLAYER_INPUT_MAX_MESSAGE_SIZE 100

namespace BoostConstants
{
	// Game Data
	extern const char* GameDataSharedMemName;
	extern const char* GameDataMutexName;
	extern const char* GameDataFlatSharedMemName;
	extern const char* GameDataFlatMutexName;

	// Player Input
	extern const char* PlayerInputQueueName;
	extern const char* PlayerInputFlatQueueName;

	// Field information
	extern const char* FieldInfoSharedMemName;
	extern const char* FieldInfoMutexName;
	extern const char* FieldInfoFlatSharedMemName;
	extern const char* FieldInfoFlatMutexName;

	// Rendering
	extern const char* RenderingFlatSharedMemName;
	extern const char* RenderingFlatMutexName;
};

#endif