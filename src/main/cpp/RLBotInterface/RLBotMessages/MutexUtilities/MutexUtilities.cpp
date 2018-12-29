#include "MutexUtilities.hpp"

#include <Windows.h>

#include "..\DebugHelper.hpp"

namespace MutexUtilities
{
	const wchar_t* pCoreMutexName = L"Local\\RLBotCore";
	const wchar_t* pBallPredictionMutexName = L"Local\\RLBotBallPrediction";

	bool waitForMutex(const wchar_t* pName)
	{
		HANDLE hMutex = NULL;

		while (!hMutex)
		{
			hMutex = OpenMutexW(SYNCHRONIZE, FALSE, pName);

			if (!hMutex)
			{
				DWORD dwLastError = GetLastError();

				if (dwLastError != ERROR_FILE_NOT_FOUND)
				{
					DEBUG_LOG("OpenMutex failed! Error code: 0x%08X\n", dwLastError);

					return false;
				}

				Sleep(100);
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

	bool WaitForMutexes()
	{
		DEBUG_LOG("Waiting for the RLBot Core and Ball Prediction Service to initialize...\n");

		if (!waitForMutex(pCoreMutexName))
			return false;

		if (!waitForMutex(pBallPredictionMutexName))
			return false;

		return true;
	}

	bool CreateCoreMutex()
	{
		return createMutex(pCoreMutexName);
	}

	bool CreateBallPredictionMutex()
	{
		return createMutex(pBallPredictionMutexName);
	}
};
