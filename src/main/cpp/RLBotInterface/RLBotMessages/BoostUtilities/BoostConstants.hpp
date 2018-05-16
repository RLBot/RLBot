#ifndef BOOSTCONSTANTS_HPP
#define BOOSTCONSTANTS_HPP

namespace BoostConstants
{
	// Game Data
	extern const char* GameDataName;
	extern const char* GameDataFlatName;

	// Player Input
	extern const char* PlayerInputQueueName;
	extern const char* PlayerInputFlatQueueName;

	// Field information
	extern const char* FieldInfoName;
	extern const char* FieldInfoFlatName;

	// Rendering
	extern const char* RenderingFlatName;

	std::string buildSharedMemName(const char* baseName);
	std::string buildMutexName(const char* baseName);
};

#endif