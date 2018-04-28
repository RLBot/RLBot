#ifndef CALLBACKPROCESSOR_HPP
#define CALLBACKPROCESSOR_HPP

#include <Messages.hpp>

typedef void(*CallbackFunction)(unsigned int id, RLBotCoreStatus status);

namespace CallbackProcessor
{
	void RegisterCallback(unsigned int id, CallbackFunction callback);
	bool Initialize();
	void Deinitialize();
}

#endif