#include "CallbackProcessor.hpp"
#include <DebugHelper.hpp>
#include <unordered_map>
#include <Windows.h>

namespace CallbackProcessor
{
	static volatile bool bTerminate = false;
	static HANDLE hProcessCallbacks = NULL;
	static MessageProcessor<CONST_CALLBACK_INPUT_SIZE>* pMessageProcessor;
	static std::unordered_map<unsigned int, CallbackFunction> callbackMap;

	RLBotCoreStatus handleCallback(MessageBase* pMessage)
	{
		CallbackMessage* pCallback = (CallbackMessage*)pMessage;
		auto it = callbackMap.find(pCallback->FunctionID);

		if (it != callbackMap.end())
		{
			it->second(pCallback->FunctionID, pCallback->Status);
			callbackMap.erase(it);
		}

		return RLBotCoreStatus::Success;
	}

	DWORD WINAPI processCallbacks(void*)
	{
		while (!bTerminate)
		{
			pMessageProcessor->ProcessMessages(true);
			Sleep(100);
		}

		return ERROR_SUCCESS;
	}

	void RegisterCallback(unsigned int id, CallbackFunction callback)
	{
		callbackMap[id] = callback;
	}

	bool Initialize()
	{
		DEBUG_LOG("Initializing the callback processor...\n");
		pMessageProcessor = new MessageProcessor<CONST_CALLBACK_INPUT_SIZE>(FileMappings::GetCallbackOutput());
		hProcessCallbacks = CreateThread(nullptr, 0, &processCallbacks, nullptr, 0, nullptr);

		if (hProcessCallbacks)
			CloseHandle(hProcessCallbacks);
		else
			DEBUG_LOG("Failed to create the ProcessCallbacks thread! Error code: %i\n", GetLastError());

		pMessageProcessor->SubscribeMessage(CallbackMessageType, &handleCallback);
		DEBUG_LOG("Successfully initialized the callback processor!\n");

		return hProcessCallbacks != NULL;
	}

	void Deinitialize()
	{
		bTerminate = true;
		WaitForSingleObject(hProcessCallbacks, 5000);
	}
}