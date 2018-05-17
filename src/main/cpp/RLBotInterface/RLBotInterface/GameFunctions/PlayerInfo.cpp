#include <CapnProto\capnproto.hpp>
#include "game_data.pb.h"
#include <DebugHelper.hpp>

#include "PlayerInfo.hpp"
#include <BoostUtilities\BoostConstants.hpp>

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

		::capnp::MallocMessageBuilder message;
		rlbot::PlayerInput::Builder capnInput = message.initRoot<rlbot::PlayerInput>();
		capnInput.setPlayerIndex(playerIndex);

		rlbot::ControllerState::Builder capnState = capnInput.initControllerState();
		capnState.setBoost(playerInput.Boost);
		capnState.setHandbrake(playerInput.Handbrake);
		capnState.setJump(playerInput.Jump);
		capnState.setPitch(playerInput.Pitch);
		capnState.setRoll(playerInput.Roll);
		capnState.setSteer(playerInput.Steer);
		capnState.setThrottle(playerInput.Throttle);
		capnState.setYaw(playerInput.Yaw);

		ByteBuffer buf = CapnConversions::toBuf(&message);
		status = UpdatePlayerInputCapnp(buf.ptr, buf.size);

		delete[] buf.ptr;
		return status;
	}

	// Proto
	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputProto(void* playerInputBinary, int protoSize)
	{
		rlbot::api::PlayerInput protoInput = rlbot::api::PlayerInput();
		protoInput.ParseFromArray(playerInputBinary, protoSize);
		rlbot::api::ControllerState protoState = protoInput.controller_state();

		::capnp::MallocMessageBuilder message;
		rlbot::PlayerInput::Builder capnInput = message.initRoot<rlbot::PlayerInput>();
		capnInput.setPlayerIndex(protoInput.player_index());

		rlbot::ControllerState::Builder capnState = capnInput.initControllerState();
		capnState.setBoost(protoState.boost());
		capnState.setHandbrake(protoState.handbrake());
		capnState.setJump(protoState.jump());
		capnState.setPitch(protoState.pitch());
		capnState.setRoll(protoState.roll());
		capnState.setSteer(protoState.steer());
		capnState.setThrottle(protoState.throttle());
		capnState.setYaw(protoState.yaw());

		ByteBuffer buf = CapnConversions::toBuf(&message);

		RLBotCoreStatus status = UpdatePlayerInputCapnp(buf.ptr, buf.size);

		delete[] buf.ptr;

		return status;
	}

	// Capn
	static BoostUtilities::QueueSender capnInputQueue(BoostConstants::PlayerInputQueueName);


	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputCapnp(void* controllerState, int protoSize)
	{
		return capnInputQueue.sendMessage(controllerState, protoSize);
	}

	// FLAT
	static BoostUtilities::QueueSender flatInputQueue(BoostConstants::PlayerInputFlatQueueName);

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputFlatbuffer(void* controllerState, int protoSize)
	{
		return flatInputQueue.sendMessage(controllerState, protoSize);
	}
}
