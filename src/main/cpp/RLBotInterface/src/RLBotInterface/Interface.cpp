#include "Interface.hpp"

#include <atomic>
#include <Messages.hpp>
#include "GameFunctions/BallPrediction.hpp"
#include "GameFunctions/GamePacket.hpp"
#include "GameFunctions/GameFunctions.hpp"
#include "GameFunctions/PlayerInfo.hpp"
#include "RenderFunctions/RenderFunctions.hpp"

#ifdef _WIN32
#include <Windows.h>
#include <timeapi.h>
#endif

#include <cerrno>
#include <thread>

namespace Interface
{
	static int SLEEP_RESOLUTION_MILLISECONDS = 1;
	std::atomic_bool bInitialized(false);

	extern "C" bool RLBOT_CORE_API IsInitialized()
	{
		return bInitialized.load();
	}

	#ifdef _WIN32
	DWORD WINAPI Initialize()
	{
		DEBUG_LOG("====================================================================\n");
		DEBUG_LOG("RLBot Core Interface\n");
		DEBUG_LOG("====================================================================\n");
		DEBUG_LOG("Initializing...\n");

		// Sets the minimum time period to 1 millisecond so that sleep is more accurate.
		// https://docs.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timebeginperiod
		timeBeginPeriod(SLEEP_RESOLUTION_MILLISECONDS);

		if (!MutexUtilities::WaitForRLBotExe())
			return EINTR;

		GameFunctions::Initialize_GamePacket();
		GameFunctions::Initialize_GameFunctions();
		GameFunctions::Initialize_PlayerInfo();
		RenderFunctions::Initialize();
		
		bInitialized = true;
		DEBUG_LOG("RLBot Core Interface has been successfully initialized!\n");

		return 0;
	}
	#endif

	#if defined(__linux__) || defined(__APPLE__)
	void Initialize()
	{
		//DEBUG_LOG("====================================================================\n");
		//DEBUG_LOG("RLBot Core Interface\n");
		//DEBUG_LOG("====================================================================\n");
		//DEBUG_LOG("Initializing...\n");

		MutexUtilities::WaitForRLBotExe();

		GameFunctions::Initialize_GamePacket();
		GameFunctions::Initialize_GameFunctions();
		GameFunctions::Initialize_PlayerInfo();
		RenderFunctions::Initialize();
		
		bInitialized = true;
		//DEBUG_LOG("RLBot Core Interface has been successfully initialized!\n");
	}
	#endif


	void Uninitialize()
	{
		// The timeEndPeriod function clears a previously set minimum timer resolution.
		// https://docs.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timeendperiod
		timeEndPeriod(SLEEP_RESOLUTION_MILLISECONDS);

		GameFunctions::Uninitialize_GamePacket();
		GameFunctions::Uninitialize_PlayerInfo();
	}
}

#ifdef _WIN32
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID)
{
	UNREFERENCED_PARAMETER(hinstDLL);

	if (fdwReason == DLL_PROCESS_ATTACH)
	{
		Interface::Initialize();

		return TRUE;
	}
	else if (fdwReason == DLL_PROCESS_DETACH)
		Interface::Uninitialize();

	return FALSE;
}
#endif

#if defined(__linux__) || defined(__APPLE__)
__attribute__((constructor)) void init(void) 
{ 
	Interface::Initialize();
}

__attribute__((destructor))  void fini(void) 
{ 
	Interface::Uninitialize();
}
#endif