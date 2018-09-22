#include <DebugHelper.hpp>
#include <rlbot_generated.h>

#include "PlayerInfo.hpp"
#include "QuickChatRateLimiter.hpp"
#include <BoostUtilities\BoostConstants.hpp>
#include <MessageTranslation\FlatbufferTranslator.hpp>

#include <chrono>
#include <thread>

#include "..\CallbackProcessor\SharedMemoryDefinitions.hpp"

namespace GameFunctions
{
	RLBotCoreStatus checkQuickChatPreset(QuickChatPreset quickChatPreset)
	{
		if (quickChatPreset < 0 || quickChatPreset > QuickChatPreset::MaxQuickChatPresets)
			return RLBotCoreStatus::InvalidQuickChatPreset;

		return RLBotCoreStatus::Success;
	}

	// FLAT
	static BoostUtilities::QueueSender quickChatQueue(BoostConstants::QuickChatFlatQueueName);
	static QuickChat::QuickChatRateLimiter quickChatRateLimiter;

	extern "C" RLBotCoreStatus RLBOT_CORE_API SendQuickChat(void* quickChatMessage, int protoSize)
	{
		auto parsedChat = flatbuffers::GetRoot<rlbot::flat::QuickChat>(quickChatMessage);
		int playerIndex = parsedChat->playerIndex();

		RLBotCoreStatus status = checkQuickChatPreset((QuickChatPreset) parsedChat->quickChatSelection());

		if (status != RLBotCoreStatus::Success)
			return status;

		RLBotCoreStatus sendStatus = quickChatRateLimiter.CanSendChat(playerIndex);
		if (sendStatus == RLBotCoreStatus::Success)
		{
			quickChatRateLimiter.RecordQuickChatSubmission(playerIndex);
			return quickChatQueue.sendMessage(quickChatMessage, protoSize);
		}
		return sendStatus;
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API SendChat(QuickChatPreset quickChatPreset, int playerIndex, bool bTeam, CallbackFunction callback, unsigned int* pID)
	{
		RLBotCoreStatus status = checkQuickChatPreset(quickChatPreset);

		if (status != RLBotCoreStatus::Success)
			return status;


		RLBotCoreStatus sendStatus = quickChatRateLimiter.CanSendChat(playerIndex);
		if (sendStatus == RLBotCoreStatus::Success)
		{
			quickChatRateLimiter.RecordQuickChatSubmission(playerIndex);
			BEGIN_GAME_FUNCTION(SendChatMessage, pSendChat);
			REGISTER_CALLBACK(pSendChat, callback, pID);
			pSendChat->QuickChatPreset = quickChatPreset;
			pSendChat->PlayerIndex = playerIndex;
			pSendChat->bTeam = bTeam;
			END_GAME_FUNCTION;

			return RLBotCoreStatus::Success;
		}
		return sendStatus;
	}

	// Player info
	RLBotCoreStatus checkInputConfiguration(PlayerInput playerInput)
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

	// Ctypes
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInput(PlayerInput playerInput, int playerIndex)
	{
		RLBotCoreStatus status = checkInputConfiguration(playerInput);

		if (status != RLBotCoreStatus::Success)
			return status;

		flatbuffers::FlatBufferBuilder builder;
		FlatbufferTranslator::inputStructToFlatbuffer(&builder, playerInput, playerIndex);
		return UpdatePlayerInputFlatbuffer(builder.GetBufferPointer(), builder.GetSize());
	}

	// FLAT
	static BoostUtilities::QueueSender flatInputQueue(BoostConstants::PlayerInputFlatQueueName);

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputFlatbuffer(void* controllerState, int protoSize)
	{
		return flatInputQueue.sendMessage(controllerState, protoSize);
	}
}
