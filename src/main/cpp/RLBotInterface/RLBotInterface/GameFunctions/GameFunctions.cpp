#include <CapnProto\capnproto.hpp>
#include "game_data.pb.h"
#include <DebugHelper.hpp>
#include <boost\interprocess\ipc\message_queue.hpp>
#include <boost/interprocess/shared_memory_object.hpp>
#include <boost/interprocess/mapped_region.hpp>
#include <boost\interprocess\sync\named_sharable_mutex.hpp>
#include <boost\interprocess\sync\sharable_lock.hpp>

#include "GameFunctions.hpp"
#include <BoostConstants\BoostConstants.hpp>

#include "..\CallbackProcessor\CallbackProcessor.hpp"

#include <chrono>
#include <thread>

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

	

	ByteBuffer fetchCapnp(boost::interprocess::shared_memory_object* shm, boost::interprocess::named_sharable_mutex* mtx)
	{
		// The lock will be released when this object goes out of scope
		boost::interprocess::sharable_lock<boost::interprocess::named_sharable_mutex> myLock(*mtx);

		boost::interprocess::offset_t size;
		shm->get_size(size);
		if (size == 0)
		{
			// Bail out early because mapped_region will freak out if size is zero.
			ByteBuffer empty;
			empty.ptr = new char[1]; // Arbitrary valid pointer to an array. We'll be calling delete[] on this later.
			empty.size = 0;
			return empty;
		}

		boost::interprocess::mapped_region region(*shm, boost::interprocess::read_only);
		unsigned char *buffer = new unsigned char[region.get_size()];
		memcpy(buffer, region.get_address(), region.get_size());

		ByteBuffer buf;
		buf.ptr = buffer;
		buf.size = region.get_size();
		return buf;
	}

	static boost::interprocess::shared_memory_object gameTickShm(boost::interprocess::open_only, BoostConstants::GameDataSharedMemName, boost::interprocess::read_only);
	static boost::interprocess::named_sharable_mutex gameTickMutex(boost::interprocess::open_only, BoostConstants::GameDataMutexName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketCapnp()
	{
		return fetchCapnp(&gameTickShm, &gameTickMutex);
	}

	static boost::interprocess::shared_memory_object fieldInfoShm(boost::interprocess::open_only, BoostConstants::FieldInfoSharedMemName, boost::interprocess::read_only);
	static boost::interprocess::named_sharable_mutex fieldInfoMutex(boost::interprocess::open_only, BoostConstants::FieldInfoMutexName);

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoCapnp()
	{
		return fetchCapnp(&fieldInfoShm, &fieldInfoMutex);
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdateLiveDataPacket(LiveDataPacket* pLiveData)
	{
		ByteBuffer capnp = UpdateLiveDataPacketCapnp();
		CapnConversions::capnpGameTickToStruct(capnp, pLiveData);
		delete[] capnp.ptr;

		ByteBuffer fieldInfo = UpdateFieldInfoCapnp();
		CapnConversions::applyFieldInfoToStruct(fieldInfo, pLiveData);
		delete[] fieldInfo.ptr;

		return RLBotCoreStatus::Success;
	}

	extern "C" ByteBuffer RLBOT_CORE_API UpdateLiveDataPacketProto()
	{
		ByteBuffer capnp = UpdateLiveDataPacketCapnp();
		return CapnConversions::capnpGameTickToProtobuf(capnp);
	}

	extern "C" ByteBuffer RLBOT_CORE_API UpdateFieldInfoProto()
	{
		ByteBuffer capnp = UpdateFieldInfoCapnp();
		return CapnConversions::capnpFieldInfoToProtobuf(capnp);
	}

	extern "C" RLBotCoreStatus RLBOT_CORE_API SetGameState(void* gameTickPacket, int protoSize, CallbackFunction callback, unsigned int* pID)
	{
		rlbot::api::GameTickPacket* protoResult = &rlbot::api::GameTickPacket();
		protoResult->ParseFromArray(gameTickPacket, protoSize);

		// TODO: convert to canproto and send to core via a message queue
		return RLBotCoreStatus::Success;
	}

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

	static interop_message_queue capnpPlayerInput(boost::interprocess::open_only, BoostConstants::PlayerInputQueueName);

	extern "C" RLBotCoreStatus RLBOT_CORE_API UpdatePlayerInputCapnp(void* controllerState, int protoSize)
	{
		bool sent = capnpPlayerInput.try_send(controllerState, protoSize, 0);
		if (!sent) {
			return RLBotCoreStatus::BufferOverfilled;
		}
		return RLBotCoreStatus::Success;
	}

	extern "C" void RLBOT_CORE_API Free(void* ptr)
	{
		free(ptr);
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