#include "capnproto.hpp"
#include "game_data.pb.h"
#define _USE_MATH_DEFINES
#include <math.h>

namespace CapnConversions {


	std::string convertString(wchar_t* w) {
		std::wstring ws(w);
		std::string str(ws.begin(), ws.end());
		return str;
	}
	

    ByteBuffer toBuf(capnp::MallocMessageBuilder* message) {
        kj::Array<capnp::word> words = capnp::messageToFlatArray(*message);
		kj::ArrayPtr<kj::byte> bytes = words.asBytes();

		// Copy to an allocated buffer
		unsigned char *buffer = new unsigned char[bytes.size()];
		memcpy(buffer, bytes.begin(), bytes.size());

        ByteBuffer buf;
		buf.ptr = buffer;
        buf.size = bytes.size();
        return buf;
    }

	rlbot::api::Vector3* convertVector(rlbot::Vector3::Reader vec) {
		auto protoVec = new rlbot::api::Vector3();
		protoVec->set_x(vec.getX());
		protoVec->set_y(vec.getY());
		protoVec->set_z(vec.getZ());

		return protoVec;
	}

	rlbot::api::Rotator* convertRotation(rlbot::Rotator::Reader rot) {
		auto protoRot = new rlbot::api::Rotator();
		protoRot->set_pitch(rot.getPitch());
		protoRot->set_yaw(rot.getYaw());
		protoRot->set_roll(rot.getRoll());

		return protoRot;
	}

	rlbot::api::Physics* allocateProtobufPhysics(rlbot::Physics::Reader capnPhysics) {
		auto protoPhysics = new rlbot::api::Physics();
		protoPhysics->set_allocated_location(convertVector(capnPhysics.getLocation()));
		protoPhysics->set_allocated_rotation(convertRotation(capnPhysics.getRotation()));
		protoPhysics->set_allocated_velocity(convertVector(capnPhysics.getVelocity()));
		protoPhysics->set_allocated_angular_velocity(convertVector(capnPhysics.getAngularVelocity()));
		return protoPhysics;
	}

	rlbot::api::Touch* allocateProtobufTouch(rlbot::Touch::Reader capnTouch) {
		auto protoTouch = new rlbot::api::Touch();
		protoTouch->set_allocated_location(convertVector(capnTouch.getLocation()));
		protoTouch->set_allocated_normal(convertVector(capnTouch.getNormal()));
		protoTouch->set_player_name(std::string(capnTouch.getPlayerName().cStr()));
		protoTouch->set_game_seconds(capnTouch.getGameSeconds());
		return protoTouch;
	}

	rlbot::api::BallInfo* allocateProtobufBall(rlbot::BallInfo::Reader capnBall) {
		auto protoBall = new rlbot::api::BallInfo();
		protoBall->set_allocated_physics(allocateProtobufPhysics(capnBall.getPhysics()));

		if (capnBall.getLatestTouch().hasValue())
		{
			protoBall->set_allocated_latest_touch(allocateProtobufTouch(capnBall.getLatestTouch().getValue()));
		}

		return protoBall;
	}

	rlbot::api::ScoreInfo* allocateProtobufScore(rlbot::ScoreInfo::Reader capnScore) {
		auto protoScore = new rlbot::api::ScoreInfo();
		
		protoScore->set_assists(capnScore.getAssists());
		protoScore->set_demolitions(capnScore.getDemolitions());
		protoScore->set_goals(capnScore.getGoals());
		protoScore->set_own_goals(capnScore.getOwnGoals());
		protoScore->set_saves(capnScore.getSaves());
		protoScore->set_score(capnScore.getScore());
		protoScore->set_shots(capnScore.getShots());

		return protoScore;
	}

	void fillProtoPlayer(rlbot::api::PlayerInfo* protoPlayer, rlbot::PlayerInfo::Reader* capnPlayer) 
	{
		protoPlayer->set_allocated_physics(allocateProtobufPhysics(capnPlayer->getPhysics()));
		protoPlayer->set_allocated_score_info(allocateProtobufScore(capnPlayer->getScoreInfo()));
		protoPlayer->set_name(capnPlayer->getName().cStr());
		protoPlayer->set_team(capnPlayer->getTeam());
		protoPlayer->set_boost(capnPlayer->getBoost());
		protoPlayer->set_jumped(capnPlayer->getJumped());
		protoPlayer->set_double_jumped(capnPlayer->getDoubleJumped());
		protoPlayer->set_is_bot(capnPlayer->getIsBot());
		protoPlayer->set_is_demolished(capnPlayer->getIsDemolished());
		protoPlayer->set_has_wheel_contact(capnPlayer->getHasWheelContact());
		protoPlayer->set_is_supersonic(capnPlayer->getIsSupersonic());
	}

	void fillProtoBoostState(rlbot::api::BoostPadState* protoBoost, rlbot::BoostPadState::Reader* capnpBoost)
	{
		protoBoost->set_is_active(capnpBoost->getIsActive());
		protoBoost->set_timer(capnpBoost->getTimer());
	}

	rlbot::api::GameInfo* canpnGameInfoToProtobuf(rlbot::GameInfo::Reader capnInfo)
	{
		auto protoInfo = new rlbot::api::GameInfo();
		protoInfo->set_game_time_remaining(capnInfo.getGameTimeRemaining());
		protoInfo->set_is_kickoff_pause(capnInfo.getIsKickoffPause());
		protoInfo->set_is_match_ended(capnInfo.getIsMatchEnded());
		protoInfo->set_is_overtime(capnInfo.getIsOvertime());
		protoInfo->set_is_round_active(capnInfo.getIsRoundActive());
		protoInfo->set_is_unlimited_time(capnInfo.getIsUnlimitedTime());
		protoInfo->set_seconds_elapsed(capnInfo.getSecondsElapsed());

		return protoInfo;
	}

	ByteBuffer capnpGameTickToProtobuf(ByteBuffer capnData)
	{
		kj::ArrayPtr<const capnp::word> arrayPtr = kj::ArrayPtr<const capnp::word>((const capnp::word*) capnData.ptr, capnData.size);
		capnp::FlatArrayMessageReader reader = capnp::FlatArrayMessageReader(arrayPtr, capnp::ReaderOptions());
		rlbot::GameTickPacket::Reader tickReader = reader.getRoot<rlbot::GameTickPacket>();


		rlbot::api::GameTickPacket* packet = new rlbot::api::GameTickPacket();

		if (tickReader.hasPlayers())
		{
			auto players = tickReader.getPlayers();

			for (int i = 0; i < players.size(); i++) {
				rlbot::PlayerInfo::Reader player = players[i];
				rlbot::api::PlayerInfo* protoCar = packet->add_players();
				fillProtoPlayer(protoCar, &player);
			}
		}


		if (tickReader.hasBoostPadStates())
		{
			auto boosts = tickReader.getBoostPadStates();

			for (int i = 0; i < boosts.size(); i++) {
				rlbot::BoostPadState::Reader boost = boosts[i];
				rlbot::api::BoostPadState* protoBoost = packet->add_boost_pad_states();
				fillProtoBoostState(protoBoost, &boost);
			}
		}

		if (tickReader.hasBall())
		{
			packet->set_allocated_ball(allocateProtobufBall(tickReader.getBall()));
		}

		if (tickReader.hasGameInfo())
		{
			packet->set_allocated_game_info(canpnGameInfoToProtobuf(tickReader.getGameInfo()));
		}


		int byte_size = packet->ByteSize();
		void* proto_binary = malloc(byte_size);
		packet->SerializeToArray(proto_binary, byte_size);

		ByteBuffer byteBuffer;
		byteBuffer.ptr = proto_binary;
		byteBuffer.size = byte_size;

		return byteBuffer;

	}

	void fillProtoBoost(rlbot::api::BoostPad* protoBoost, rlbot::BoostPad::Reader capnpBoost)
	{
		protoBoost->set_allocated_location(convertVector(capnpBoost.getLocation()));
		protoBoost->set_is_full_boost(capnpBoost.getIsFullBoost());
	}

	void fillProtoGoal(rlbot::api::GoalInfo* protoGoal, rlbot::GoalInfo::Reader capnGoal)
	{
		protoGoal->set_allocated_location(convertVector(capnGoal.getLocation()));
		protoGoal->set_allocated_direction(convertVector(capnGoal.getDirection()));
		protoGoal->set_team_num(capnGoal.getTeamNum());
	}

	ByteBuffer capnpFieldInfoToProtobuf(ByteBuffer capnData)
	{
		kj::ArrayPtr<const capnp::word> arrayPtr = kj::ArrayPtr<const capnp::word>((const capnp::word*) capnData.ptr, capnData.size);
		capnp::FlatArrayMessageReader reader = capnp::FlatArrayMessageReader(arrayPtr, capnp::ReaderOptions());
		rlbot::FieldInfo::Reader fieldInfoReader = reader.getRoot<rlbot::FieldInfo>();


		rlbot::api::FieldInfo* fieldInfo = new rlbot::api::FieldInfo();

		if (fieldInfoReader.hasGoals())
		{
			auto goals = fieldInfoReader.getGoals();

			for (int i = 0; i < goals.size(); i++) {
				rlbot::GoalInfo::Reader goalInfo = goals[i];
				rlbot::api::GoalInfo* protoGoal = fieldInfo->add_goals();
				fillProtoGoal(protoGoal, goalInfo);
			}
		}

		if (fieldInfoReader.hasBoostPads())
		{
			auto boosts = fieldInfoReader.getBoostPads();

			for (int i = 0; i < boosts.size(); i++) {
				rlbot::BoostPad::Reader boost = boosts[i];
				rlbot::api::BoostPad* protoBoost = fieldInfo->add_boost_pads();
				fillProtoBoost(protoBoost, boost);
			}
		}

		int byte_size = fieldInfo->ByteSize();
		void* proto_binary = malloc(byte_size);
		fieldInfo->SerializeToArray(proto_binary, byte_size);

		ByteBuffer byteBuffer;
		byteBuffer.ptr = proto_binary;
		byteBuffer.size = byte_size;

		return byteBuffer;

	}

	// Will try to deserialize a rlbot::PlayerInput from the buffer.
    IndexedPlayerInput* bufferToPlayerInput(ByteBuffer buf)
    {

        kj::ArrayPtr<const capnp::word> arrayPtr = kj::ArrayPtr<const capnp::word>((const capnp::word*) buf.ptr, buf.size);
        capnp::FlatArrayMessageReader reader = capnp::FlatArrayMessageReader(arrayPtr, capnp::ReaderOptions());
        rlbot::PlayerInput::Reader inputReader = reader.getRoot<rlbot::PlayerInput>();
		rlbot::ControllerState::Reader cStateReader = inputReader.getControllerState();

        IndexedPlayerInput* playerInput = new IndexedPlayerInput;
		playerInput->Index = inputReader.getPlayerIndex();
		playerInput->PlayerInput.Boost = cStateReader.getBoost();
        playerInput->PlayerInput.Handbrake = cStateReader.getHandbrake();
        playerInput->PlayerInput.Jump = cStateReader.getJump();
        playerInput->PlayerInput.Pitch = cStateReader.getPitch();
        playerInput->PlayerInput.Roll = cStateReader.getRoll();
        playerInput->PlayerInput.Steer = cStateReader.getSteer();
        playerInput->PlayerInput.Throttle = cStateReader.getThrottle();
        playerInput->PlayerInput.Yaw = cStateReader.getYaw();

        return playerInput;
    }

	void fillStructName(std::string str, wchar_t structStr[])
	{
		std::wstring widestr = std::wstring(str.begin(), str.end());
		const wchar_t* widecstr = widestr.c_str();

		memcpy(structStr, widecstr, std::min(sizeof(PlayerConfiguration::Name), (wcslen(widecstr) + 1) * sizeof(wchar_t))); // Copy over the string
		structStr[sizeof(PlayerConfiguration::Name) / sizeof(wchar_t) - 1] = L'\0'; // Null terminate the string

	}

	void fillVector3Struct(rlbot::Vector3::Reader capnVec, PyStruct::Vector3* structVec) 
	{
		structVec->X = capnVec.getX();
		structVec->Y = capnVec.getY();
		structVec->Z = capnVec.getZ();
	}

	int convertToURot(float radians)
	{
		return roundf(radians * 32768 / M_PI);
	}

	void fillRotatorStruct(rlbot::Rotator::Reader capnVec, PyStruct::Rotator* structVec)
	{
		structVec->Pitch = convertToURot(capnVec.getPitch());
		structVec->Yaw = convertToURot(capnVec.getYaw());
		structVec->Roll = convertToURot(capnVec.getRoll());
	}

	void fillScoreStruct(rlbot::ScoreInfo::Reader capnScore, ScoreInfo* structScore)
	{
		structScore->Assists = capnScore.getAssists();
		structScore->Demolitions = capnScore.getDemolitions();
		structScore->Goals = capnScore.getGoals();
		structScore->OwnGoals = capnScore.getOwnGoals();
		structScore->Saves = capnScore.getSaves();
		structScore->Score = capnScore.getScore();
		structScore->Shots = capnScore.getShots();
	}

	void fillPlayerStruct(rlbot::PlayerInfo::Reader* capnPlayer, PlayerInfo* structPlayer)
	{
		auto physics = capnPlayer->getPhysics();
		fillVector3Struct(physics.getLocation(), &structPlayer->Location);
		fillRotatorStruct(physics.getRotation(), &structPlayer->Rotation);
		fillVector3Struct(physics.getVelocity(), &structPlayer->Velocity);
		fillVector3Struct(physics.getAngularVelocity(), &structPlayer->AngularVelocity);

		
		structPlayer->Boost = capnPlayer->getBoost();
		structPlayer->Bot = capnPlayer->getIsBot();
		structPlayer->Demolished = capnPlayer->getIsDemolished();
		structPlayer->DoubleJumped = capnPlayer->getDoubleJumped();
		structPlayer->Jumped = capnPlayer->getJumped();
		fillStructName(capnPlayer->getName().cStr(), structPlayer->Name);
		structPlayer->OnGround = capnPlayer->getHasWheelContact();
		fillScoreStruct(capnPlayer->getScoreInfo(), &structPlayer->Score);
		structPlayer->SuperSonic = capnPlayer->getIsSupersonic();
		structPlayer->Team = capnPlayer->getTeam();
	}

	void fillBoostStruct(rlbot::BoostPadState::Reader* capnBoost, BoostInfo* structBoost)
	{
		structBoost->Active = capnBoost->getIsActive();
		structBoost->Timer = capnBoost->getTimer();

		// Location is unavailable from BoostPadState. It will need to be added later from FieldInfo.
	}

	void fillTouchStruct(rlbot::BallInfo::LatestTouch::Reader capnTouch, Touch* structTouch)
	{
		if (capnTouch.hasValue())
		{
			auto touch = capnTouch.getValue();
			fillStructName(touch.getPlayerName(), structTouch->PlayerName);
			fillVector3Struct(touch.getLocation(), &structTouch->HitLocation);
			fillVector3Struct(touch.getNormal(), &structTouch->HitNormal);
			structTouch->TimeSeconds = touch.getGameSeconds();

		} 
		else
		{
			fillStructName(std::string(""), structTouch->PlayerName);
		}
	}

	void fillBallStruct(rlbot::BallInfo::Reader capnBall, BallInfo* structBall)
	{
		auto physics = capnBall.getPhysics();
		fillVector3Struct(physics.getLocation(), &structBall->Location);
		fillRotatorStruct(physics.getRotation(), &structBall->Rotation);
		fillVector3Struct(physics.getVelocity(), &structBall->Velocity);
		fillVector3Struct(physics.getAngularVelocity(), &structBall->AngularVelocity);

		fillTouchStruct(capnBall.getLatestTouch(), &structBall->LatestTouch);
	}

	void fillGameInfoStruct(rlbot::GameInfo::Reader capnGameInfo, GameInfo* structGameInfo)
	{
		structGameInfo->BallHasBeenHit = !capnGameInfo.getIsKickoffPause();
		structGameInfo->GameTimeRemaining = capnGameInfo.getGameTimeRemaining();
		structGameInfo->MatchEnded = capnGameInfo.getIsMatchEnded();
		structGameInfo->OverTime = capnGameInfo.getIsOvertime();
		structGameInfo->RoundActive = capnGameInfo.getIsRoundActive();
		structGameInfo->TimeSeconds = capnGameInfo.getSecondsElapsed();
		structGameInfo->UnlimitedTime = capnGameInfo.getIsUnlimitedTime();
	}

	void capnpGameTickToStruct(ByteBuffer capnData, LiveDataPacket* liveDataPacket)
	{
		kj::ArrayPtr<const capnp::word> arrayPtr = kj::ArrayPtr<const capnp::word>((const capnp::word*) capnData.ptr, capnData.size);
		capnp::FlatArrayMessageReader reader = capnp::FlatArrayMessageReader(arrayPtr, capnp::ReaderOptions());
		rlbot::GameTickPacket::Reader tickReader = reader.getRoot<rlbot::GameTickPacket>();

		if (tickReader.hasPlayers())
		{
			auto players = tickReader.getPlayers();
			liveDataPacket->NumCars = players.size();
			for (int i = 0; i < players.size(); i++) {
				fillPlayerStruct(&players[i], &liveDataPacket->GameCars[i]);
			}
		}

		if (tickReader.hasBoostPadStates()) 
		{
			auto boosts = tickReader.getBoostPadStates();
			liveDataPacket->NumBoosts = boosts.size();
			for (int i = 0; i < boosts.size(); i++) {
				fillBoostStruct(&boosts[i], &liveDataPacket->GameBoosts[i]);
			}
		}

		if (tickReader.hasBall())
		{
			fillBallStruct(tickReader.getBall(), &liveDataPacket->GameBall);
		}
		if (tickReader.hasGameInfo())
		{
			fillGameInfoStruct(tickReader.getGameInfo(), &liveDataPacket->GameInfo);
		}
	}

	void applyFieldInfoToStruct(ByteBuffer capnData, LiveDataPacket* pLiveData)
	{
		kj::ArrayPtr<const capnp::word> arrayPtr = kj::ArrayPtr<const capnp::word>((const capnp::word*) capnData.ptr, capnData.size);
		capnp::FlatArrayMessageReader reader = capnp::FlatArrayMessageReader(arrayPtr, capnp::ReaderOptions());
		rlbot::FieldInfo::Reader fieldReader = reader.getRoot<rlbot::FieldInfo>();

		if (!fieldReader.hasBoostPads()) 
		{
			return;
		}

		auto boostPads = fieldReader.getBoostPads();
		for (int i = 0; i < boostPads.size() && i < pLiveData->NumBoosts; i++)
		{
			fillVector3Struct(boostPads[i].getLocation(), &pLiveData->GameBoosts[i].Location);
		}
	}

}
