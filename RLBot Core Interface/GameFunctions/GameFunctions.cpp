#include "GameFunctions.hpp"

#include "..\CallbackProcessor\CallbackProcessor.hpp"

#define BEGIN_GAME_FUNCTION(structName, name)	GameInput* pGameInput = FileMappings::GetGameInput(); \
												pGameInput->Lock(); \
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
	//static MessageBase* pGameMessage = nullptr;

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

#ifdef ENABLE_PROTO
	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketProto()
	{
		LiveDataPacket packet = LiveDataPacket();
		UpdateLiveDataPacket(&packet);

		rlbot::api::GameTickPacket* protoResult = ProtoConversions::convert(&packet);
		int byte_size = protoResult->ByteSize();
		CompiledGameTickPacket proto_binary = malloc(byte_size);
		protoResult->SerializeToArray(proto_binary, byte_size);

		ByteBuffer byteBuffer;
		byteBuffer.ptr = proto_binary;
		byteBuffer.size = byte_size;

		return byteBuffer;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API SetGameState(CompiledGameTickPacket gameTickPacket, int protoSize, CallbackFunction callback, unsigned int* pID)
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

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputProto(CompiledControllerState controllerState, int protoSize, int playerIndex)
	{
		// decode player input proto
		rlbot::api::ControllerState controllerStateProto = rlbot::api::ControllerState();
		controllerStateProto.ParseFromArray(controllerState, protoSize);
		PlayerInput* playerInput = ProtoConversions::convert(&controllerStateProto);

		return UpdatePlayerInput(*playerInput, playerIndex);
	}

	extern "C" void RLBOT_CORE_API Free(void* ptr)
	{
		free(ptr);
	}
#endif

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateMatchDataPacket(MatchDataPacket* pMatchData)
	{
		memcpy(pMatchData, &FileMappings::GetMatchData()->MatchDataPacket, sizeof(MatchDataPacket));

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API StartMatch(PlayerConfiguration playerConfiguration[CONST_MaxPlayers], MatchSettings matchSettings, MutatorSettings mutatorSettings, CallbackFunction callback, unsigned int* pID)
	{
		int numPlayers = matchSettings.numPlayers;
		RLBotCoreStatus status = checkPlayerConfiguration(playerConfiguration, numPlayers);

		if (status != RLBotCoreStatus::Success)
			return status;

		BEGIN_GAME_FUNCTION(StartMatchMessage, pStartMatch);
		REGISTER_CALLBACK(pStartMatch, callback, pID);

		for (size_t i = 0; i < numPlayers; i++)
		{
			pStartMatch->PlayerConfiguration[i] = playerConfiguration[i];
		}

		pStartMatch->MatchSettings = matchSettings;
		pStartMatch->MutatorSettings = mutatorSettings;
		END_GAME_FUNCTION;

		return RLBotCoreStatus::Success;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInput(const PlayerInput& playerInput, int playerIndex)
	{
		RLBotCoreStatus status = checkInputConfiguration(playerInput);

		if (status != RLBotCoreStatus::Success)
			return status;

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