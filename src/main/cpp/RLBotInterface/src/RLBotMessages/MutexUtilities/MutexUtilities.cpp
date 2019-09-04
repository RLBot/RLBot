#include "MutexUtilities.hpp"

#ifdef _WIN32
#include <windows.h>
#endif
#ifdef __linux__
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/shm.h>
#include <unistd.h>
#include <fcntl.h>
#endif
#include <thread>
#include <cerrno>
#include <iostream>

#include "DebugHelper.hpp"

namespace MutexUtilities
{


	#ifdef _WIN32
	#define CHAR wchar_t
	const CHAR* pRLBotExeMutexName = L"Local\\RLBotExe";
	const CHAR* pBallPredictionMutexName = L"Local\\RLBotBallPrediction";
	#endif

	#ifdef __linux__
	#define CHAR char
	const CHAR* pRLBotExeMutexName = "RLBotExeMutex";
	const CHAR* pBallPredictionMutexName = "RLBotBallPredictionMutex";
	#endif

	bool checkMutexExists(const CHAR* pName)
	{
		#ifdef _WIN32
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
		#endif

		#ifdef __linux__
		int handle = shm_open(pName, O_RDWR, S_IRWXU|S_IRWXO);

		if (handle == -1)
		{
			if (errno != ENOENT)
				printf("shm_open failed! Error code: %i\n", errno);

			return false;
		}
		else
		{
			close(handle);
			return true;
		}
		#endif
	}

	bool waitForMutex(const CHAR* pName)
	{
		#ifdef _WIN32
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
		#endif

		#ifdef __linux__
		while (!checkMutexExists(pName))
		{
			std::this_thread::sleep_for(std::chrono::microseconds(100));
		}

		return true;
		#endif
	}

	bool createMutex(const CHAR* pName)
	{
		#ifdef _WIN32
		HANDLE hMutex = CreateMutexW(NULL, TRUE, pName);

		if (!hMutex)
		{
			DEBUG_LOG("CreateMutex failed! Error code: 0x%08X\n", GetLastError());

			return false;
		}

		return true;
		#endif

		#ifdef __linux__
		int handle = shm_open(pName, O_RDWR|O_CREAT, S_IRWXU|S_IRWXO);

		if (handle == -1)
		{
			printf("shm_open failed! Error code: %i\n", errno);
			return false;
		}

		shmctl(handle, IPC_RMID, 0);

		return true;
		#endif
	}

	void freeMutex(const CHAR* pName)
	{
		// windows should free these automatically.

		#ifdef __linux__
		shm_unlink(pName);
		#endif 
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

	void FreeRLBotExeMutex()
	{
		freeMutex(pRLBotExeMutexName);
	}

	void FreeBallPredictionMutex()
	{
		freeMutex(pBallPredictionMutexName);
	}
};
