#include "FileMappings.hpp"

namespace FileMappings
{
	static LPVOID lpMappedInputData = nullptr,
		lpMappedOutputData = nullptr;

	static HANDLE hInputFileMapping = NULL,
		hOutputFileMapping = NULL;

	HANDLE createOrOpenFileMapping(DWORD size, LPCSTR lpName)
	{
		HANDLE hMapFile = OpenFileMappingA(FILE_MAP_WRITE, FALSE, lpName);

		if (!hMapFile)
			hMapFile = CreateFileMappingA(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, 0, size, lpName);

		if (!hMapFile)
			DEBUG_LOG("CreateFileMapping failed! Error code: %i\n", GetLastError());

		return hMapFile;
	}

	LPVOID mapViewOfFile(HANDLE hFileMappingObject, DWORD size)
	{
		LPVOID lpMappedData = MapViewOfFile(hFileMappingObject, FILE_MAP_WRITE, 0, 0, size);

		if (!lpMappedData)
		{
			CloseHandle(hFileMappingObject);
			DEBUG_LOG("MapViewOfFile failed! Error code: %i\n", GetLastError());
		}

		return lpMappedData;
	}

	GameInput* GetGameInput()
	{
		if (!lpMappedInputData)
			return nullptr;

		return &((GameInputData*)lpMappedInputData)->GameInput;
	}

	RenderInput* GetRenderInput()
	{
		if (!lpMappedInputData)
			return nullptr;

		return &((GameInputData*)lpMappedInputData)->RenderInput;
	}

	LiveDataWrapper* GetLiveData()
	{
		if (!lpMappedOutputData)
			return nullptr;

		return &((GameOutputData*)lpMappedOutputData)->LiveData;
	}

	MatchDataWrapper* GetMatchData()
	{
		if (!lpMappedOutputData)
			return nullptr;

		return &((GameOutputData*)lpMappedOutputData)->MatchData;
	}

	CallbackOutput* GetCallbackOutput()
	{
		if (!lpMappedOutputData)
			return nullptr;

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

		hInputFileMapping = createOrOpenFileMapping(sizeof(GameInputData), "Local\\RLBotInput");

		if (!hInputFileMapping)
			return false;

		lpMappedInputData = mapViewOfFile(hInputFileMapping, sizeof(GameInputData));

		if (!lpMappedInputData)
			return false;

		DEBUG_LOG("Initializing the output file mapping...\n");

		hOutputFileMapping = createOrOpenFileMapping(sizeof(GameOutputData), "Local\\RLBotOutput");

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