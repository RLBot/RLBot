#include <DebugHelper.hpp>
#include <boost\interprocess\ipc\message_queue.hpp>
#include <boost\interprocess\shared_memory_object.hpp>
#include <boost\interprocess\mapped_region.hpp>
#include <boost\interprocess\sync\named_sharable_mutex.hpp>
#include <boost\interprocess\sync\sharable_lock.hpp>

#include "GameFunctions.hpp"
#include <BoostUtilities\BoostConstants.hpp>
#include <BoostUtilities\BoostUtilities.hpp>
#include <MessageTranslation\FlatbufferTranslator.hpp>
#include <MessageTranslation\StructToRLBotFlatbuffer.hpp>

#include <chrono>
#include <thread>

namespace GameFunctions
{
	BoostUtilities::QueueSender* pGameStateQueue = nullptr;
	BoostUtilities::QueueSender* pMatchControlQueue = nullptr;

	void Initialize_GameFunctions()
	{
		pGameStateQueue = new BoostUtilities::QueueSender(BoostConstants::GameStateFlatQueueName);
		pMatchControlQueue = new BoostUtilities::QueueSender(BoostConstants::MatchControlQueueName);
	}

	extern "C" void RLBOT_CORE_API Free(void* ptr)
	{
		free(ptr);
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API SetGameState(void* gameStateData, int size)
	{
		if (!pGameStateQueue)
		{
			return RLBotCoreStatus::NotInitialized;
		}
		return pGameStateQueue->sendMessage(gameStateData, size);
	}

	// Start match

	bool isValidName(wchar_t* pName)
	{
		for (int i = 0; i < sizeof(PlayerConfiguration::Name) / sizeof(wchar_t); i++)
		{
			wchar_t wideChar = pName[i];

			if (wideChar == L'\0')
				return true;

			if (wideChar < L' ' || wideChar > L'~')
				return false;
		}

		return false;
	}

	RLBotCoreStatus checkPlayerConfiguration(PlayerConfiguration playerConfiguration[CONST_MaxPlayers], int numPlayers)
	{
		if (numPlayers < 0 || numPlayers > CONST_MaxPlayers)
			return RLBotCoreStatus::InvalidNumPlayers;

		for (int i = 0; i < numPlayers; i++)
		{
			PlayerConfiguration& playerConfig = playerConfiguration[i];

			if (playerConfig.Bot)
			{
				if (!playerConfig.RLBotControlled)
				{
					if (playerConfig.BotSkill < 0.0f || playerConfig.BotSkill > 1.0f)
						return RLBotCoreStatus::InvalidBotSkill;
				}

				if (!isValidName(playerConfig.Name))
					RLBotCoreStatus::InvalidName;
			}

			if (playerConfig.Team < 0 || playerConfig.Team > 1)
				return RLBotCoreStatus::InvalidTeam;

			if (playerConfig.TeamColorID < 0 || playerConfig.TeamColorID > 69)
				return RLBotCoreStatus::InvalidTeamColorID;

			if (playerConfig.CustomColorID < 0 || playerConfig.CustomColorID > 104)
				return RLBotCoreStatus::InvalidTeamColorID;

			//Todo: Add items validation
		}

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API StartMatch(MatchSettings matchSettings)
	{
		int numPlayers = matchSettings.NumPlayers;
		//ToDo: Check the other settings
		RLBotCoreStatus status = checkPlayerConfiguration(matchSettings.PlayerConfiguration, numPlayers);

		if (status != RLBotCoreStatus::Success)
			return status;

		flatbuffers::FlatBufferBuilder builder;
		StructToRLBotFlatbuffer::BuildStartMatchMessage(&builder, matchSettings);

		return pMatchControlQueue->sendMessage(builder.GetBufferPointer(), builder.GetSize());
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API StartMatchFlatbuffer(void* startMatchSettings, int size)
	{
		ByteBuffer buf;
		buf.ptr = startMatchSettings;
		buf.size = size;

		MatchSettings matchSettings = { 0 };

		FlatbufferTranslator::translateToMatchSettingsStruct(buf, &matchSettings);

		return StartMatch(matchSettings);
	}
}