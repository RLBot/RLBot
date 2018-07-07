#include <DebugHelper.hpp>
#include <flatbuffers\flatbuffers.h>

#include "PlayerInfo.hpp"
#include <BoostUtilities\BoostConstants.hpp>
#include <MessageTranslation\FlatbufferTranslator.hpp>

#include <chrono>
#include <thread>

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

	extern "C" RLBotCoreStatus RLBOT_CORE_API SendQuickChat(void* quickChatMessage, int protoSize)
	{
		return quickChatQueue.sendMessage(quickChatMessage, protoSize);
	}

	// Player info
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

	// Ctypes
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInput(const PlayerInput& playerInput, int playerIndex)
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
