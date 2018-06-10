#ifndef FILEMAPPINGS_HPP
#define FILEMAPPINGS_HPP

#include <Windows.h>

#include "../PacketStructs/PacketStructs.hpp"

#define LOCKED													1
#define UNLOCKED												0

namespace FileMappings
{
	GameInput* GetGameInput();
	RenderInput* GetRenderInput();
	CallbackOutput* GetCallbackOutput();
	void Lock(void* pSharedMem);
	void Unlock(void* pSharedMem);
	bool Initialize();
	void Deinitialize();
};

#endif