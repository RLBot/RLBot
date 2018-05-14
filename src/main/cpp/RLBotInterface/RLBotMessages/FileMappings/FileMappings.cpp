#include "FileMappings.hpp"
#include "..\DebugHelper.hpp"

#include <wtshintapi.h>

namespace FileMappings
{
	static LPVOID lpMappedInputData = nullptr,
		lpMappedOutputData = nullptr;

	static HANDLE hInputFileMapping = NULL,
		hOutputFileMapping = NULL;

	HANDLE createFileMapping(DWORD size, LPWSTR lpName)
	{
		HANDLE hMapFile = CreateFileMappingW(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, 0, size, lpName);

		if (!hMapFile)
			DEBUG_LOG("CreateFileMapping failed! Error code: 0x%08X\n", GetLastError());

		return hMapFile;
	}

	LPVOID mapViewOfFile(HANDLE hFileMappingObject, DWORD size)
	{
		LPVOID lpMappedData = MapViewOfFile(hFileMappingObject, FILE_MAP_READ | FILE_MAP_WRITE, 0, 0, size);

		if (!lpMappedData)
		{
			DEBUG_LOG("MapViewOfFile failed! Error code: 0x%08X\n", GetLastError());
			CloseHandle(hFileMappingObject);
		}

		return lpMappedData;
	}

	GameInput* GetGameInput()
	{
		return &((GameInputData*)lpMappedInputData)->GameInput;
	}

	RenderInput* GetRenderInput()
	{
		return &((GameInputData*)lpMappedInputData)->RenderInput;
	}

	CallbackOutput* GetCallbackOutput()
	{
		return &((GameOutputData*)lpMappedOutputData)->CallbackOutput;
	}

	void Lock(void* pSharedMem)
	{
		while (InterlockedCompareExchange((unsigned int*)pSharedMem, LOCKED, UNLOCKED) != UNLOCKED)
			Sleep(0);
	}

	void Unlock(void* pSharedMem)
	{
		InterlockedExchange((unsigned int*)pSharedMem, UNLOCKED);
	}

	bool Initialize()
	{
		DEBUG_LOG("Initializing the input file mapping...\n");
		hInputFileMapping = createFileMapping(sizeof(GameInputData), L"Local\\RLBotInput");

		if (!hInputFileMapping)
			return false;

		lpMappedInputData = mapViewOfFile(hInputFileMapping, sizeof(GameInputData));

		if (!lpMappedInputData)
			return false;

		DEBUG_LOG("Initializing the output file mapping...\n");
		hOutputFileMapping = createFileMapping(sizeof(GameOutputData), L"Local\\RLBotOutput");

		if (!hOutputFileMapping)
			return false;

		lpMappedOutputData = mapViewOfFile(hOutputFileMapping, sizeof(GameOutputData));

		if (!lpMappedOutputData)
			return false;

		return true;
	}

	void Deinitialize()
	{
		DEBUG_LOG("Deinitializing the file mappings...\n");

		if (lpMappedInputData)
			UnmapViewOfFile(lpMappedInputData);

		if (hInputFileMapping)
			CloseHandle(hInputFileMapping);

		if (lpMappedOutputData)
			UnmapViewOfFile(lpMappedOutputData);

		if (hOutputFileMapping)
			CloseHandle(hOutputFileMapping);

		DEBUG_LOG("Successfully deinitialized the file mappings!\n");
	}
}