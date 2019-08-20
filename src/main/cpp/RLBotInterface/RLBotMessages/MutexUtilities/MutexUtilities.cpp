#include "MutexUtilities.hpp"

#include <Windows.h>
#include <thread>
#include <cerrno>

#include "..\DebugHelper.hpp"

namespace MutexUtilities
{
	const wchar_t* pRLBotExeMutexName = L"Local\\RLBotExe";
	const wchar_t* pBallPredictionMutexName = L"Local\\RLBotBallPrediction";

	bool checkMutexExists(const wchar_t* pName)
	{
		HANDLE hMutex = OpenMutexW(SYNCHRONIZE, FALSE, pName);

		if (!hMutex)
		{
			DWORD dwLastError = GetLastError();

			if (dwLastError != ENOENT)
				DEBUG_LOG("OpenMutex failed! Error code: 0x%08X\n", dwLastError);

			return false;
		}

		CloseHandle(hMutex);

		return true;
	}

	bool waitForMutex(const wchar_t* pName)
	{
		HANDLE hMutex = NULL;

		while (!hMutex)
		{
			hMutex = OpenMutexW(SYNCHRONIZE, FALSE, pName);

			if (!hMutex)
			{
				DWORD dwLastError = GetLastError();

				if (dwLastError != ENOENT)
				{
					DEBUG_LOG("OpenMutex failed! Error code: 0x%08X\n", dwLastError);

					return false;
				}
				std::this_thread::sleep_for(std::chrono::microseconds(100));
			}
		}

		CloseHandle(hMutex);

		return true;
	}

	bool createMutex(const wchar_t* pName)
	{
		HANDLE hMutex = CreateMutexW(NULL, TRUE, pName);

		if (!hMutex)
		{
			DEBUG_LOG("CreateMutex failed! Error code: 0x%08X\n", GetLastError());

			return false;
		}

		return true;
	}

	bool WaitForRLBotExe()
	{
		DEBUG_LOG("Waiting for RLBot.exe to initialize...\n");

		return waitForMutex(pRLBotExeMutexName);
	}

	bool IsBallPredictionServiceRunning()
	{
		return checkMutexExists(pBallPredictionMutexName);
	}

	bool CreateRLBotExeMutex()
	{
		return createMutex(pRLBotExeMutexName);
	}

	bool CreateBallPredictionMutex()
	{
		return createMutex(pBallPredictionMutexName);
	}
};
