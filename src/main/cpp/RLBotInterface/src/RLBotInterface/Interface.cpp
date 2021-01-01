#include "Interface.hpp"

#include <atomic>
#include <algorithm>
#include <Messages.hpp>
#include "GameFunctions/BallPrediction.hpp"
#include "GameFunctions/GamePacket.hpp"
#include "GameFunctions/GameFunctions.hpp"
#include "GameFunctions/PlayerInfo.hpp"
#include "RenderFunctions/RenderFunctions.hpp"
#include "RLBotSockets/bot_client.hpp"
#include "Logging/Log.h"

#ifdef _WIN32
#include <Windows.h>
#include <timeapi.h>
#include <libloaderapi.h>
#endif

#include <cerrno>

namespace Interface
{
	static unsigned int TARGET_SLEEP_RESOLUTION_MILLISECONDS = 1;
	unsigned int actualSleepResolution;

	std::atomic_bool bInitialized(false);

	extern "C" bool RLBOT_CORE_API IsInitialized()
	{
		return bInitialized.load();
	}

	extern "C" bool RLBOT_CORE_API IsReadyForCommunication()
	{
		auto bot_client = BotClientStatic::botClientInstance();
		return bot_client != nullptr && bot_client->is_connected;
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
		// https://docs.microsoft.com/en-us/windows/win32/multimedia/obtaining-and-setting-timer-resolution
		TIMECAPS tc;

		if (timeGetDevCaps(&tc, sizeof(TIMECAPS)) == TIMERR_NOERROR)
		{
			actualSleepResolution = std::min(std::max(tc.wPeriodMin, TARGET_SLEEP_RESOLUTION_MILLISECONDS), tc.wPeriodMax);
		}
		else
		{
			actualSleepResolution = 1;
		}

		timeBeginPeriod(actualSleepResolution);

		bInitialized = true;

		char filename_buffer[200];
		GetModuleFileNameA(nullptr, filename_buffer, 200);

		int pid = GetCurrentProcessId();

		char dll_name[250];
		sprintf(dll_name, "%i - %s", pid, filename_buffer);
		RLBotLog::set_prefix(std::string(dll_name));

		return 0;
	}
	#endif

	#if defined(__linux__) || defined(__APPLE__)
	void Initialize()
	{
		//DEBUG_LOG("====================================================================\n");
		//DEBUG_LOG("RLBot Core Interface\n");
		//DEBUG_LOG("====================================================================\n");
		bInitialized = true;
	}
	#endif


	void Uninitialize()
	{
		#ifdef _WIN32
		// The timeEndPeriod function clears a previously set minimum timer resolution.
		// https://docs.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timeendperiod
		timeEndPeriod(actualSleepResolution);
		#endif
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
