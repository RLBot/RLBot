#include "Interface.hpp"

#include <atomic>
#include <Messages.hpp>

#include "CallbackProcessor\CallbackProcessor.hpp"

namespace Interface
{
	static std::atomic_bool bInitialized = false;

	extern "C" bool RLBOT_CORE_API IsInitialized()
	{
		return bInitialized;
	}

	void Callback(unsigned int id, RLBotCoreStatus status)
	{
		DEBUG_LOG("SendChat callback has been called! ID: %i - Status: %i\n", id, status);
	}

	DWORD WINAPI Initialize(void*)
	{
#ifdef _DEBUG
		AllocConsole();
		AttachConsole(GetCurrentProcessId());
		freopen("CONOUT$", "w", stdout);
#endif

		DEBUG_LOG("====================================================================\n");
		DEBUG_LOG("RLBot Core Interface\n");
		DEBUG_LOG("====================================================================\n");
		DEBUG_LOG("Initializing...\n");

		if (!FileMappings::Initialize())
			return ERROR_FUNCTION_FAILED;

		if (!CallbackProcessor::Initialize())
			return ERROR_FUNCTION_FAILED;

		bInitialized = true;
		DEBUG_LOG("RLBot Core Interface has been successfully initialized!\n");

		while (1)
		{
			if (GetAsyncKeyState(VK_NUMPAD0) & 1)
			{
				RenderFunctions::BeginRendering();
				/*RenderFunctions::DrawLine2D(10, 10, 500, 500, { 0, 0, 0xFF, 0xFF });
				RenderFunctions::DrawLine3D(Vector3(0, 0, 0), Vector3(0, 300, 300), { 0, 0, 0xFF, 0xFF });*/
				RenderFunctions::DrawString2D(600, 380, 10, 10, Color(0, 0, 0xFF, 0xFF), L"YOU SUCK!!!");
				RenderFunctions::EndRendering();
			}

			if (GetAsyncKeyState(VK_NUMPAD1) & 1)
			{
				RenderFunctions::BeginRendering();
				RenderFunctions::EndRendering();
			}

			unsigned int id;

			if (GetAsyncKeyState(VK_NUMPAD2) & 1)
			{
				PlayerConfiguration playerConfiguration[CONST_MaxPlayers];
				playerConfiguration[0].Bot = true;
				playerConfiguration[0].RLBotControlled = true;
				playerConfiguration[0].BotSkill = 1.0f;
				wcscpy(playerConfiguration[0].Name, L"Test");
				playerConfiguration[0].Team = 0;
				playerConfiguration[0].TeamColorID = 0;
				playerConfiguration[0].CustomColorID = 0;
				playerConfiguration[0].CarID = 257;

				playerConfiguration[1].Bot = true;
				playerConfiguration[1].RLBotControlled = true;
				playerConfiguration[1].HumanIndex = 0;
				wcscpy(playerConfiguration[1].Name, L"ccman32");
				playerConfiguration[1].Team = 1;
				playerConfiguration[1].TeamColorID = 0;
				playerConfiguration[1].CustomColorID = 0;
				playerConfiguration[1].CarID = 257;

				GameFunctions::StartMatch(playerConfiguration, 2);
			}

			if (GetAsyncKeyState(VK_NUMPAD3) & 1)
			{
				PlayerInput input;
				input.Boost = true;
				input.Throttle = 1.0f;
				GameFunctions::UpdatePlayerInput(input, 0);
			}

			if (GetAsyncKeyState(VK_NUMPAD4) & 1)
			{
				GameFunctions::SendChat(QuickChatPreset::Compliments_NiceShot, 1, false, &Callback, &id);
			}

			if (GetAsyncKeyState(VK_NUMPAD5) & 1)
			{
				GameFunctions::SendChat(QuickChatPreset::Compliments_GreatPass, 1, false, &Callback, &id);
			}

			if (GetAsyncKeyState(VK_NUMPAD6) & 1)
			{
				GameFunctions::SendChat(QuickChatPreset::Information_NeedBoost, 0, true, &Callback, &id);
			}

			if (GetAsyncKeyState(VK_NUMPAD7) & 1)
			{
				GameFunctions::SendChat(QuickChatPreset::Reactions_Siiiick, 1, false, &Callback, &id);
			}
		}

		return ERROR_SUCCESS;
	}

	void Uninitialize()
	{
		bInitialized = false;
		CallbackProcessor::Deinitialize();
		FileMappings::Deinitialize();

#ifdef _DEBUG
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