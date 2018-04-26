#include <CapnProto\capnproto.hpp>
#include <Protobuf\ProtoConversions.hpp>
#include <boost\interprocess\ipc\message_queue.hpp>

#include "GameFunctions.hpp"

#include "..\CallbackProcessor\CallbackProcessor.hpp"

/*
This typedef is advice from one of the boost maintainers on how to make message queues work between 32 and 64 bit processes.
It looks pretty janky. I believe the reason it's not "fixed" in the library is that it can't be done consistently on windows vs linux.

"In general I regret putting message_queue in Interprocess, as IMHO it's not good enough to be in the library. Some people find it useful, though."
https://lists.boost.org/Archives/boost/2014/06/214746.php
*/
typedef boost::interprocess::message_queue_t< boost::interprocess::offset_ptr<void, boost::int32_t, boost::uint64_t>> interop_message_queue;


#define BEGIN_GAME_FUNCTION(structName, name)	GameInput* pGameInput = FileMappings::GetGameInput(); \
												pGameInput->Lock(); \
												CHECK_BUFFER_OVERFILLED(pGameInput, true); \
												BEGIN_FUNCTION(structName, name, pGameInput)

#define END_GAME_FUNCTION						END_FUNCTION(pGameInput); \
												pGameInput->Unlock()

#define REGISTER_CALLBACK(name, callback, id)	if (callback) \
												{ \
													CallbackProcessor::RegisterCallback(name->ID, callback); \
												} \
												if (id) \
												{ \
													*id = name->ID; \
												}

namespace GameFunctions
{
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

			if (playerConfig.TeamColorID < 0 || playerConfig.TeamColorID > 27)
				return RLBotCoreStatus::InvalidTeamColorID;

			if (playerConfig.CustomColorID < 0 || playerConfig.CustomColorID > 104)
				return RLBotCoreStatus::InvalidTeamColorID;

			//Todo: Add items validation
		}

		return RLBotCoreStatus::Success;
	}

	RLBotCoreStatus checkInputConfiguration(const PlayerInput& playerInput)
	{
		if (playerInput.Throttle < -1.0f || playerInput.Throttle > 1.0f)
			return RLBotCoreStatus::InvalidThrottle;

		if (playerInput.Steer < -1.0f || playerInput.Steer > 1.0f)
			return RLBotCoreStatus::InvalidSteer;

		if (playerInput.Pitch < -1.0f || playerInput.Pitch > 1.0f)
			return RLBotCoreStatus::InvalidPitch;

		if (playerInput.Yaw < -1.0f || playerInput.Yaw > 1.0f)
			return RLBotCoreStatus::InvalidYaw;

		if (playerInput.Roll < -1.0f || playerInput.Roll > 1.0f)
			return RLBotCoreStatus::InvalidRoll;

		return RLBotCoreStatus::Success;
	}

	RLBotCoreStatus checkQuickChatPreset(QuickChatPreset quickChatPreset)
	{
		if (quickChatPreset < 0 || quickChatPreset > QuickChatPreset::MaxQuickChatPresets)
			return RLBotCoreStatus::InvalidQuickChatPreset;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateLiveDataPacket(LiveDataPacket* pLiveData)
	{
		memcpy(pLiveData, &FileMappings::GetLiveData()->LiveDataPacket, sizeof(LiveDataPacket));

		return RLBotCoreStatus::Success;
	}

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketProto()
	{
		LiveDataPacket packet = LiveDataPacket();
		UpdateLiveDataPacket(&packet);

		rlbot::api::GameTickPacket* protoResult = ProtoConversions::convert(&packet);
		int byte_size = protoResult->ByteSize();
		void* proto_binary = malloc(byte_size);
		protoResult->SerializeToArray(proto_binary, byte_size);

		ByteBuffer byteBuffer;
		byteBuffer.ptr = proto_binary;
		byteBuffer.size = byte_size;

		return byteBuffer;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API SetGameState(void* gameTickPacket, int protoSize, CallbackFunction callback, unsigned int* pID)
	{
		rlbot::api::GameTickPacket* protoResult = &rlbot::api::GameTickPacket();
		protoResult->ParseFromArray(gameTickPacket, protoSize);
		LiveDataPacket* packet = &LiveDataPacket();
		UpdateLiveDataPacket(packet);
		RLBotCoreStatus status = ProtoConversions::convert(protoResult, packet);

		if (status != RLBotCoreStatus::Success)
			return status;

		BEGIN_GAME_FUNCTION(SetGameStateMessage, pSetGameData);
		REGISTER_CALLBACK(pSetGameData, callback, pID);

		pSetGameData->GameState = *packet;

		END_GAME_FUNCTION;
		return RLBotCoreStatus::Success;
	}

	static interop_message_queue protobufPlayerInput(boost::interprocess::open_only, "protobuf_player_update_queue");

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputProto(void* playerInputBinary, int protoSize)
	{
		// TODO: instead of sending protobuf directly, translate to capnproto first.

		bool sent = protobufPlayerInput.try_send(playerInputBinary, protoSize, 0);
		if (!sent) {
			DEBUG_LOG("Failed to send player input protobuf!\n", sent);
			return RLBotCoreStatus::BufferOverfilled;
		}
		
		return RLBotCoreStatus::Success;
	}

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketCapnp()
	{
		LiveDataPacket packet = LiveDataPacket();
		UpdateLiveDataPacket(&packet);
		return CapnConversions::liveDataPacketToBuffer(&packet);
	}

	static interop_message_queue capnpPlayerInput(boost::interprocess::open_only, "capnp_player_update_queue");

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputCapnp(void* controllerState, int protoSize)
	{
		bool sent = capnpPlayerInput.try_send(controllerState, protoSize, 0);
		if (!sent) {
			DEBUG_LOG("Failed to send player input capnproto!\n", sent);
			return RLBotCoreStatus::BufferOverfilled;
		}
		return RLBotCoreStatus::Success;
	}

	extern "C" void RLBOT_CORE_API Free(void* ptr)
	{
		free(ptr);
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateMatchDataPacket(MatchDataPacket* pMatchData)
	{
		memcpy(pMatchData, &FileMappings::GetMatchData()->MatchDataPacket, sizeof(MatchDataPacket));

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API StartMatch(MatchSettings matchSettings, CallbackFunction callback, unsigned int* pID)
	{
		int numPlayers = matchSettings.NumPlayers;
		//ToDo: Check the other settings
		RLBotCoreStatus status = checkPlayerConfiguration(matchSettings.PlayerConfiguration, numPlayers);

		if (status != RLBotCoreStatus::Success)
			return status;

		BEGIN_GAME_FUNCTION(StartMatchMessage, pStartMatch);
		REGISTER_CALLBACK(pStartMatch, callback, pID);
		pStartMatch->MatchSettings = matchSettings;
		END_GAME_FUNCTION;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInput(const PlayerInput& playerInput, int playerIndex)
	{
		RLBotCoreStatus status = checkInputConfiguration(playerInput);

		if (status != RLBotCoreStatus::Success)
			return status;

		// TODO: Translate to capnproto and use a boost message queue instead.

		BEGIN_GAME_FUNCTION(UpdatePlayerInputMessage, pUpdatePlayerInput);
		pUpdatePlayerInput->PlayerInput = playerInput;
		pUpdatePlayerInput->PlayerIndex = playerIndex;
		END_GAME_FUNCTION;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API SendChat(QuickChatPreset quickChatPreset, int playerIndex, bool bTeam, CallbackFunction callback, unsigned int* pID)
	{
		RLBotCoreStatus status = checkQuickChatPreset(quickChatPreset);

		if (status != RLBotCoreStatus::Success)
			return status;

		BEGIN_GAME_FUNCTION(SendChatMessage, pSendChat);
		REGISTER_CALLBACK(pSendChat, callback, pID);
		pSendChat->QuickChatPreset = quickChatPreset;
		pSendChat->PlayerIndex = playerIndex;
		pSendChat->bTeam = bTeam;
		END_GAME_FUNCTION;

		return RLBotCoreStatus::Success;
	}
}