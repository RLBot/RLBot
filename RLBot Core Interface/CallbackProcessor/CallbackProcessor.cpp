#include "CallbackProcessor.hpp"

#include <unordered_map>
#include <Windows.h>

namespace CallbackProcessor
{
	static volatile bool bTerminate = false;
	static HANDLE hProcessCallbacks = NULL;
	static MessageProcessor messageProcessor;
	static CallbackOutput* pCallbackOutput = nullptr;
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
			FileMappings::Lock(pCallbackOutput);
			messageProcessor.ProcessMessages((MessageBase*)&pCallbackOutput->Data[0], pCallbackOutput->NumMessages);
			pCallbackOutput->NumMessages = 0;
			FileMappings::Unlock(pCallbackOutput);
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
		pCallbackOutput = FileMappings::GetCallbackOutput();
		hProcessCallbacks = CreateThread(nullptr, 0, &processCallbacks, nullptr, 0, nullptr);

		if (hProcessCallbacks)
			CloseHandle(hProcessCallbacks);
		else
			DEBUG_LOG("Failed to create the ProcessCallbacks thread! Error code: %i\n", GetLastError());

		messageProcessor.SubscribeMessage(CallbackMessageType, &handleCallback);
		DEBUG_LOG("Successfully initialized the callback processor!\n");

		return hProcessCallbacks != NULL;
	}

	void Deinitialize()
	{
		bTerminate = true;
		WaitForSingleObject(hProcessCallbacks, 5000);
	}
}