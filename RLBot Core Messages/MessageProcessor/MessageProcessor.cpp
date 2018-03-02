#include "MessageProcessor.hpp"

#include "..\FileMappings\FileMappings.hpp"
#include "..\MessageDefines\MessageDefines.hpp"
#include "..\MessageStructs\CallbackMessages.hpp"

#define BEGIN_CALLBACK_FUNCTION(structName, name)	if (!pCallbackOutput) \
													{ \
														pCallbackOutput = FileMappings::GetCallbackOutput(); \
													} \
													FileMappings::Lock(pCallbackOutput); \
													if (!pCallbackMessage || pCallbackOutput->NumMessages == 0) \
													{ \
														RESET_MESSAGE_POINTER(pCallbackMessage, pCallbackOutput); \
													} \
													BEGIN_FUNCTION(structName, name, pCallbackMessage)

#define END_CALLBACK_FUNCTION						END_FUNCTION(pCallbackOutput, pCallbackMessage); \
													FileMappings::Unlock(pCallbackOutput)

static CallbackOutput* pCallbackOutput = nullptr;
static MessageBase* pCallbackMessage = nullptr;

void MessageProcessor::SubscribeMessage(MessageType type, MessageHandler handler)
{
	messageHandlerMap[type] = handler;
}

void MessageProcessor::ProcessMessages(MessageBase* pFirst, size_t numMessages)
{
	MessageBase* pCurrent = pFirst;
	size_t current = 0;

	while (current < numMessages)
	{
		auto result = messageHandlerMap.find(pCurrent->Type);

		if (result != messageHandlerMap.end())
		{
			RLBotCoreStatus returnValue = result->second(pCurrent);

			if (pCurrent->HasCallback)
			{
				BEGIN_CALLBACK_FUNCTION(CallbackMessage, pCallback);
				pCallback->FunctionID = pCurrent->ID;
				pCallback->Status = returnValue;
				END_CALLBACK_FUNCTION;
			}

			pCurrent = (MessageBase*)((unsigned char*)pCurrent + GetSizeFunctions[pCurrent->Type](pCurrent));
		}
		
		current++;
	}
}