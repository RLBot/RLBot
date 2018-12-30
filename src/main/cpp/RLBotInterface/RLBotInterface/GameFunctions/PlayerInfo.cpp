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
	BoostUtilities::QueueSender* pQuickChatQueue = nullptr;
	BoostUtilities::QueueSender* pFlatInputQueue = nullptr;

	void Initialize_PlayerInfo()
	{
		pQuickChatQueue = new BoostUtilities::QueueSender(BoostConstants::QuickChatFlatQueueName);
		pFlatInputQueue = new BoostUtilities::QueueSender(BoostConstants::PlayerInputFlatQueueName);
	}

	RLBotCoreStatus checkQuickChatPreset(QuickChatPreset quickChatPreset)
	{
		if (quickChatPreset < 0 || quickChatPreset >= QuickChatPreset::MaxQuickChatPresets)
			return RLBotCoreStatus::InvalidQuickChatPreset;

		return RLBotCoreStatus::Success;
	}

	// FLAT
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
			return pQuickChatQueue->sendMessage(quickChatMessage, protoSize);
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
		flatbuffers::FlatBufferBuilder builder;
		FlatbufferTranslator::inputStructToFlatbuffer(&builder, playerInput, playerIndex);
		RLBotCoreStatus status = UpdatePlayerInputFlatbuffer(builder.GetBufferPointer(), builder.GetSize());

		if (status != RLBotCoreStatus::Success)
			return status;

		// We're validating the input *after* sending it to the core dll because the core dll
		// is going to clamp it for us with no issues. We're reporting validation errors to
		// users just for their information because it might help them discover faulty logic.
		return checkInputConfiguration(playerInput);
	}

	// FLAT
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputFlatbuffer(void* controllerState, int protoSize)
	{
		RLBotCoreStatus status = pFlatInputQueue->sendMessage(controllerState, protoSize);

		if (status != RLBotCoreStatus::Success)
			return status;

		// We're validating the input *after* sending it to the core dll because the core dll
		// is going to clamp it for us with no issues. We're reporting validation errors to
		// users just for their information because it might help them discover faulty logic.
		PlayerInput playerInput;
		FlatbufferTranslator::inputStructFromFlatbuffer(controllerState, playerInput);
		return checkInputConfiguration(playerInput);
	}
}
