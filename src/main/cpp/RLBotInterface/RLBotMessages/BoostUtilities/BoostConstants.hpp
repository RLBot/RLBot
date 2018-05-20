#ifndef BOOSTCONSTANTS_HPP
#define BOOSTCONSTANTS_HPP

namespace BoostConstants
{
	// Game Data
	extern const char* GameDataFlatName;

	// Player Input
	extern const char* PlayerInputFlatQueueName;

	// Field information
	extern const char* FieldInfoFlatName;

	// Rendering
	extern const char* RenderingFlatQueueName;

	// Chat
	extern const char* QuickChatFlatQueueName;

	std::string buildSharedMemName(const char* baseName);
	std::string buildMutexName(const char* baseName);
};

#endif