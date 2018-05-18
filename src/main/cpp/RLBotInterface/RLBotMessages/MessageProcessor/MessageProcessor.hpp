#ifndef MESSAGEPROCESSOR_HPP
#define MESSAGEPROCESSOR_HPP

#include <unordered_map>

#include "..\ErrorCodes\ErrorCodes.hpp"
#include "..\FileMappings\FileMappings.hpp"
#include "..\MessageDefines\MessageDefines.hpp"
#include "..\MessageStructs\CallbackMessages.hpp"
#include "..\MessageStructs\Message.hpp"

//ToDo: Think of a better solution
#define BEGIN_CALLBACK_FUNCTION(structName, name)	CallbackOutput* pCallbackOutput = FileMappings::GetCallbackOutput(); \
													pCallbackOutput->Lock(); \
													if (pCallbackOutput->IsBufferOverfilled()) \
													{ \
														pCallbackOutput->Unlock(); \
														break; \
													} \
													BEGIN_FUNCTION(structName, name, pCallbackOutput)

#define END_CALLBACK_FUNCTION						END_FUNCTION(pCallbackOutput); \
													pCallbackOutput->Unlock()

typedef RLBotCoreStatus (*MessageHandler)(MessageBase* pMessage);

template<unsigned int size>
class MessageProcessor
{
private:
	std::unordered_map<MessageType, MessageHandler> messageHandlerMap;
	MessageStorage<size>* pStorage;

public:
	MessageProcessor(MessageStorage<size>* pStorage)
	{
		this->pStorage = pStorage;
	}

	void SubscribeMessage(MessageType type, MessageHandler handler)
	{
		messageHandlerMap[type] = handler;
	}

	RLBotCoreStatus callMessage(MessageType type, MessageBase* base) {
		auto result = messageHandlerMap.find(type);

		if (result != messageHandlerMap.end())
		{
			return result->second(base);
		}
		return RLBotCoreStatus::InvalidGameValues;
	}

	void ProcessMessages(bool resetOffset)
	{
		pStorage->Lock();

		for (
			auto it = pStorage->Begin();
			it != pStorage->End();
			it++
			)
		{
			//ToDo: Execute only if the callback buffer is not overfilled?
			RLBotCoreStatus returnValue = callMessage(it->Type, it.GetCurrentMessage());

			if (it->HasCallback)
			{
				BEGIN_CALLBACK_FUNCTION(CallbackMessage, pCallback);
				pCallback->FunctionID = it->ID;
				pCallback->Status = returnValue;
				END_CALLBACK_FUNCTION;
			}
		}

		if (resetOffset)
			pStorage->Reset();

		pStorage->Unlock();
	}
};

#undef BEGIN_CALLBACK_FUNCTION
#undef END_CALLBACK_FUNCTION

#endif