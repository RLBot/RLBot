#include "Interface.hpp"

#include <atomic>
#include <Messages.hpp>

#include "CallbackProcessor\CallbackProcessor.hpp"
#include "GameFunctions\BallPrediction.hpp"
#include "GameFunctions\GamePacket.hpp"
#include "GameFunctions\GameFunctions.hpp"
#include "GameFunctions\PlayerInfo.hpp"
#include "RenderFunctions\RenderFunctions.hpp"

#include <Windows.h>

#include <cerrno>

namespace Interface
{
	std::atomic_bool bInitialized(false);

	extern "C" bool RLBOT_CORE_API IsInitialized()
	{
		return bInitialized.load();
	}

	DWORD WINAPI Initialize(void*)
	{
#ifdef _DEBUG && _WIN32
		AllocConsole();
		AttachConsole(GetCurrentProcessId());
		freopen("CONOUT$", "w", stdout);
#endif
		DEBUG_LOG("====================================================================\n");
		DEBUG_LOG("RLBot Core Interface\n");
		DEBUG_LOG("====================================================================\n");
		DEBUG_LOG("Initializing...\n");

		if (!MutexUtilities::WaitForCore())
			return EINTR;

		if (!FileMappings::Initialize())
			return EINTR;

		if (!CallbackProcessor::Initialize())
			return EINTR;

		GameFunctions::Initialize_GamePacket();
		GameFunctions::Initialize_GameFunctions();
		GameFunctions::Initialize_PlayerInfo();
		RenderFunctions::Initialize();
		
		bInitialized = true;
		DEBUG_LOG("RLBot Core Interface has been successfully initialized!\n");

		return 0;
	}

	void Uninitialize()
	{
		CallbackProcessor::Deinitialize();
		FileMappings::Deinitialize();

#ifdef _DEBUG && _WIN32
		FreeConsole();
#endif
	}
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID)
{
	UNREFERENCED_PARAMETER(hinstDLL);

	if (fdwReason == DLL_PROCESS_ATTACH)
	{
		//Run the initialization in a new thread
		HANDLE hInitialize = CreateThread(nullptr, 0, &Interface::Initialize, nullptr, 0, nullptr);

		if (hInitialize)
		{
			CloseHandle(hInitialize);

			return TRUE;
		}
	}
	else if (fdwReason == DLL_PROCESS_DETACH)
		Interface::Uninitialize();

	return FALSE;
}