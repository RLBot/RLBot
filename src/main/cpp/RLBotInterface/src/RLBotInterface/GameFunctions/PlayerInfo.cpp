#include <DebugHelper.hpp>
#include <rlbot_generated.h>

#include "PlayerInfo.hpp"
#include "QuickChatRateLimiter.hpp"
#include <MessageTranslation/FlatbufferTranslator.hpp>
#include "MessageStructs/QuickChatStructs.hpp"
#include "RLBotSockets/bot_client.hpp"
#include "GameFunctions/GamePacket.hpp"

#include <chrono>
#include <thread>
#include <deque>
#include <shared_mutex>

#include <stdlib.h>


namespace GameFunctions
{

	static std::deque<QuickChatMessage> message_queue;
	static int next_quick_chat_id = 0;
	static std::shared_mutex quick_chat_mutex;


	ByteBuffer createQuickChatFlatMessage(int botIndex, int teamIndex, int lastMessageIndex)
	{
		flatbuffers::FlatBufferBuilder builder(400);

		std::vector<flatbuffers::Offset<rlbot::flat::QuickChat>> messageOffsets;

		for (auto it = message_queue.rbegin(); it != message_queue.rend(); ++it) {
			auto msg = *it;
			
			if (lastMessageIndex >= msg.MessageIndex)
				break;

			if (msg.PlayerIndex == botIndex)
				continue;

			if (msg.TeamOnly && msg.TeamIndex != teamIndex)
				continue;

			auto offset = rlbot::flat::CreateQuickChat(builder,
				(rlbot::flat::QuickChatSelection)msg.QuickChatSelection,
				msg.PlayerIndex,
				msg.TeamOnly,
				msg.MessageIndex,
				msg.TimeStamp);

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
			std::string controller_state_message((char *)quickChatMessage, protoSize);
			BotClientStatic::botClientInstance()->write(controller_state_message, TcpClient::DataType::rlbot_quick_chat);
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

	void appendReceivedChatMessage(std::string flatbuffer_message) {

		auto packet = GameFunctions::UpdateLiveDataPacketFlatbuffer();
		const auto packet_flatbuffer = flatbuffers::GetRoot<rlbot::flat::GameTickPacket>(packet.ptr);

		const rlbot::flat::QuickChat* new_message = flatbuffers::GetRoot<rlbot::flat::QuickChat>(flatbuffer_message.data());
		QuickChatMessage message;
		message.MessageIndex = next_quick_chat_id++;
		message.PlayerIndex = new_message->playerIndex();
		message.TeamOnly = new_message->teamOnly();
		message.TeamIndex = packet_flatbuffer->players()->Get(message.PlayerIndex)->team();
		message.QuickChatSelection = new_message->quickChatSelection();
		message.TimeStamp = new_message->timeStamp();

		std::unique_lock lock(quick_chat_mutex);
		if (message_queue.size() == MAX_QUICKCHAT_QUEUE_SIZE)
			message_queue.pop_front();

		message_queue.push_back(message);
	}

	extern "C" ByteBuffer RLBOT_CORE_API ReceiveChat(int botIndex, int teamIndex, int lastMessageIndex)
	{
		std::shared_lock lock(quick_chat_mutex);
		return createQuickChatFlatMessage(botIndex, teamIndex, lastMessageIndex);
	}

	// Player info
	RLBotCoreStatus checkInputConfiguration(PlayerInput playerInput)
	{
		if (playerInput.throttle < -1.0f || playerInput.throttle > 1.0f)
			return RLBotCoreStatus::InvalidThrottle;

		if (playerInput.steer < -1.0f || playerInput.steer > 1.0f)
			return RLBotCoreStatus::InvalidSteer;

		if (playerInput.pitch < -1.0f || playerInput.pitch > 1.0f)
			return RLBotCoreStatus::InvalidPitch;

		if (playerInput.yaw < -1.0f || playerInput.yaw > 1.0f)
			return RLBotCoreStatus::InvalidYaw;

		if (playerInput.roll < -1.0f || playerInput.roll > 1.0f)
			return RLBotCoreStatus::InvalidRoll;

		return RLBotCoreStatus::Success;
	}

	// Ctypes
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInput(PlayerInput playerInput, int playerIndex)
	{
		flatbuffers::FlatBufferBuilder builder;
		FlatbufferTranslator::inputStructToFlatbuffer(&builder, playerInput, playerIndex);
		RLBotCoreStatus status = UpdatePlayerInputFlatbuffer(builder.GetBufferPointer(), builder.GetSize());
		return status;
	}

	// FLAT
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputFlatbuffer(void* controllerState, int protoSize)
	{
		if (!BotClientStatic::botClientInstance())
		{
			return RLBotCoreStatus::NotInitialized;
		}

		PlayerInput playerInput;
		FlatbufferTranslator::inputStructFromFlatbuffer(controllerState, playerInput);

		// Doing the validation first to make sure there is no exception reading from the flatbuffer.
		auto validation_result = checkInputConfiguration(playerInput);

		// Send the message even if it's invalid, because out-of-range steering etc can be clamped in core.
		// The validation result will just manifest as a warning.
		std::string controller_state_message((char *)controllerState, protoSize);
		BotClientStatic::botClientInstance()->write(controller_state_message, TcpClient::DataType::rlbot_player_input);

		return validation_result;
	}
}