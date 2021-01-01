#include <DebugHelper.hpp>
#include <boost/interprocess/ipc/message_queue.hpp>
#include <boost/interprocess/shared_memory_object.hpp>
#include <boost/interprocess/mapped_region.hpp>
#include <boost/interprocess/sync/named_sharable_mutex.hpp>
#include <boost/interprocess/sync/sharable_lock.hpp>

#include "GameFunctions.hpp"
#include <MessageTranslation/FlatbufferTranslator.hpp>
#include <MessageTranslation/StructToRLBotFlatbuffer.hpp>
#include <flatbuffers/flatbuffers.h>
#include <rlbot_generated.h>

#include <chrono>
#include <thread>
#include "RLBotSockets/bot_client.hpp"

namespace GameFunctions
{

	extern "C" void RLBOT_CORE_API Free(void* ptr)
	{
		free(ptr);
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API SetGameState(void* gameStateData, int size)
	{
		std::string game_state_message((char *)gameStateData, size);
		BotClientStatic::botClientInstance()->write(game_state_message, TcpClient::DataType::rlbot_state_setting);
		return RLBotCoreStatus::Success;
	}

	// Start match

	bool isValidName(wchar_t* pName)
	{
		for (int i = 0; i < sizeof(PlayerConfiguration::name) / sizeof(wchar_t); i++)
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

			if (playerConfig.bot)
			{
				if (!playerConfig.rlbotControlled)
				{
					if (playerConfig.botSkill < 0.0f || playerConfig.botSkill > 1.0f)
						return RLBotCoreStatus::InvalidBotSkill;
				}

				if (!isValidName(playerConfig.name))
					RLBotCoreStatus::InvalidName;
			}

			if (playerConfig.team < 0 || playerConfig.team > 1)
				return RLBotCoreStatus::InvalidTeam;

			if (playerConfig.teamColorID < 0 || playerConfig.teamColorID > 69)
				return RLBotCoreStatus::InvalidTeamColorID;

			if (playerConfig.customColorID < 0 || playerConfig.customColorID > 104)
				return RLBotCoreStatus::InvalidTeamColorID;

			//Todo: Add items validation
		}

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API StartMatch(MatchSettings matchSettings)
	{
		int numPlayers = matchSettings.numPlayers;
		//ToDo: Check the other settings
		RLBotCoreStatus status = checkPlayerConfiguration(matchSettings.playerConfiguration, numPlayers);

		if (status != RLBotCoreStatus::Success)
			return status;

		flatbuffers::FlatBufferBuilder builder;
		StructToRLBotFlatbuffer::BuildStartMatchMessage(&builder, matchSettings);
		std::string start_match_string((char *) builder.GetBufferPointer(), builder.GetSize());
		BotClientStatic::botClientInstance()->write(start_match_string, TcpClient::DataType::rlbot_match_settings);

		return RLBotCoreStatus::Success;
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

	inline boost::asio::ip::address localhost = boost::asio::ip::address::from_string("127.0.0.1");
	boost::asio::io_context ioc;

	void run_ioc(int port) {
		ioc.run();
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API StartTcpCommunication(
	        int port, bool wantsBallPredictions, bool wantsQuickChat, bool wantsGameMessages) {
		DEBUG_LOG("Beginning StartTcp.\n");
		BotClientStatic::initBotClient(port, &ioc, wantsBallPredictions, wantsQuickChat, wantsGameMessages);
		std::thread io_thread(run_ioc, port);
		io_thread.detach();

		DEBUG_LOG("Returning from StartTcp.\n");
		return RLBotCoreStatus::Success;
	}
}