#include <DebugHelper.hpp>
#include <rlbot_generated.h>

#include "PlayerInfo.hpp"
#include "QuickChatRateLimiter.hpp"
#include <BoostUtilities\BoostConstants.hpp>
#include <MessageTranslation\FlatbufferTranslator.hpp>
#include "../../RLBotMessages/MessageStructs/QuickChatStructs.hpp"

#include <chrono>
#include <thread>

#include <stdlib.h>

ByteBuffer createQuickChatFlatMessage(QuickChatQueue queue, int botIndex, int teamIndex, int lastMessageIndex)
{
	flatbuffers::FlatBufferBuilder builder(400);

	std::vector<flatbuffers::Offset<rlbot::flat::QuickChat>> messageOffsets;

	for (int i = queue.Count - 1; i >= 0; i--)
	{
		if (lastMessageIndex >= queue.Messages[i].MessageIndex)
			break;

		if (queue.Messages[i].PlayerIndex == botIndex)
			continue;

		if (queue.Messages[i].TeamOnly && queue.Messages[i].TeamIndex != teamIndex)
			continue;

		auto offset = rlbot::flat::CreateQuickChat(builder,
			(rlbot::flat::QuickChatSelection)queue.Messages[i].QuickChatSelection,
			queue.Messages[i].PlayerIndex,
			queue.Messages[i].TeamOnly,
			queue.Messages[i].MessageIndex,
			queue.Messages[i].TimeStamp);

		messageOffsets.push_back(offset);
	}

	auto vectorOffset = builder.CreateVector(messageOffsets);

	auto root = rlbot::flat::CreateQuickChatMessages(builder, vectorOffset);

	builder.Finish(root);

	ByteBuffer flat;
	flat.ptr = new unsigned char[builder.GetSize()];
	flat.size = builder.GetSize();

	memcpy(flat.ptr, builder.GetBufferPointer(), flat.size);

	return flat;
}


namespace GameFunctions
{
	BoostUtilities::QueueSender* pQuickChatQueue = nullptr;
	BoostUtilities::QueueSender* pFlatInputQueue = nullptr;

	BoostUtilities::SharedMemReader* pQuickChatReader = nullptr;

	void Initialize_PlayerInfo()
	{
		pQuickChatQueue = new BoostUtilities::QueueSender(BoostConstants::QuickChatFlatQueueName);
		pFlatInputQueue = new BoostUtilities::QueueSender(BoostConstants::PlayerInputFlatQueueName);

		pQuickChatReader = new BoostUtilities::SharedMemReader(BoostConstants::QuickChatDistributionName);
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
		if (!pQuickChatQueue)
		{
			return RLBotCoreStatus::NotInitialized;
		}

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

	extern "C" RLBotCoreStatus RLBOT_CORE_API SendChat(QuickChatPreset quickChatPreset, int playerIndex, bool bTeam)
	{
		flatbuffers::FlatBufferBuilder builder;
		auto chat = rlbot::flat::CreateQuickChat(builder, (rlbot::flat::QuickChatSelection) quickChatPreset, playerIndex, bTeam);
		builder.Finish(chat);

		return SendQuickChat(builder.GetBufferPointer(), builder.GetSize());
	}

	extern "C" ByteBuffer RLBOT_CORE_API ReceiveChat(int botIndex, int teamIndex, int lastMessageIndex)
	{
		if (!pQuickChatReader)
		{
			return ByteBuffer{ 0 };
		}

		ByteBuffer queue_data = pQuickChatReader->fetchData();
		if (queue_data.size > 0)
		{
			QuickChatQueue queue = *(QuickChatQueue*)(queue_data.ptr);
			ByteBuffer return_buffer = createQuickChatFlatMessage(queue, botIndex, teamIndex, lastMessageIndex);
			delete[] queue_data.ptr;
			return return_buffer;
		}
		else
		{
			return ByteBuffer{ 0 };
		}
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
		if (!pFlatInputQueue)
		{
			return RLBotCoreStatus::NotInitialized;
		}

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