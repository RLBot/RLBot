#include "capnproto.hpp"


namespace CapnConversions {

    

	void populateVector3(rlbot::Vector3::Builder capnVec, PyStruct::Vector3 structVec) {
		capnVec.setX(structVec.X);
		capnVec.setY(structVec.Y);
		capnVec.setZ(structVec.Z);
	}

	void populateRotation(rlbot::Rotator::Builder capnRot, PyStruct::Rotator structRot) {
		capnRot.setPitch(structRot.Pitch);
		capnRot.setYaw(structRot.Yaw);
		capnRot.setRoll(structRot.Roll);
	}

	std::string convertString(wchar_t* w) {
		std::wstring ws(w);
		std::string str(ws.begin(), ws.end());
		return str;
	}

	void populateTouch(rlbot::Touch::Builder capnTouch, Touch structTouch) {
		populateVector3(capnTouch.initLocation(), structTouch.HitLocation);
		populateVector3(capnTouch.initNormal(), structTouch.HitNormal);
		capnTouch.setGameSeconds(structTouch.TimeSeconds);
		capnTouch.setPlayerName(convertString(structTouch.PlayerName));
	}

	void populateBall(rlbot::BallInfo::Builder capnBall, BallInfo structBall) {
		populateVector3(capnBall.initLocation(), structBall.Location);
		populateRotation(capnBall.initRotation(), structBall.Rotation);
		populateVector3(capnBall.initVelocity(), structBall.Velocity);
		populateVector3(capnBall.initAngularVelocity(), structBall.AngularVelocity);
		populateTouch(capnBall.initLatestTouch(), structBall.LatestTouch);
	}

	void populateScore(rlbot::ScoreInfo::Builder capnScore, ScoreInfo structScore) {
		capnScore.setAssists(structScore.Assists);
		capnScore.setDemolitions(structScore.Demolitions);
		capnScore.setGoals(structScore.Goals);
		capnScore.setOwnGoals(structScore.OwnGoals);
		capnScore.setSaves(structScore.Saves);
		capnScore.setScore(structScore.Score);
		capnScore.setShots(structScore.Shots);
	}

	void populatePlayer(rlbot::PlayerInfo::Builder capnPlayer, PlayerInfo structPlayer) {
		populateVector3(capnPlayer.initLocation(), structPlayer.Location);
		populateRotation(capnPlayer.initRotation(), structPlayer.Rotation);
		populateVector3(capnPlayer.initVelocity(), structPlayer.Velocity);
		populateVector3(capnPlayer.initAngularVelocity(), structPlayer.AngularVelocity);
		populateScore(capnPlayer.initScoreInfo(), structPlayer.Score);
		capnPlayer.setName(convertString(structPlayer.Name));
		capnPlayer.setTeam(structPlayer.Team);
		capnPlayer.setBoost(structPlayer.Boost);
		capnPlayer.setJumped(structPlayer.Jumped);
		capnPlayer.setDoubleJumped(structPlayer.DoubleJumped);
		capnPlayer.setIsBot(structPlayer.Bot);
		capnPlayer.setIsDemolished(structPlayer.Demolished);
		capnPlayer.setIsMidair(!structPlayer.OnGround);
		capnPlayer.setIsSupersonic(structPlayer.SuperSonic);
	}

	void populateBoost(rlbot::BoostInfo::Builder capnBoost, BoostInfo structBoost) {
		capnBoost.setIsActive(structBoost.Active);
		populateVector3(capnBoost.initLocation(), structBoost.Location);
		capnBoost.setTimer(structBoost.Timer);
	}

	void populateGameInfo(rlbot::GameInfo::Builder capnInfo, GameInfo structInfo) {
		capnInfo.setGameTimeRemaining(structInfo.GameTimeRemaining);
		capnInfo.setIsKickoffPause(!structInfo.BallHasBeenHit);
		capnInfo.setIsMatchEnded(structInfo.MatchEnded);
		capnInfo.setIsOvertime(structInfo.OverTime);
		capnInfo.setIsRoundActive(structInfo.RoundActive);
		capnInfo.setIsUnlimitedTime(structInfo.UnlimitedTime);
		capnInfo.setSecondsElapsed(structInfo.TimeSeconds);
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

	ByteBuffer liveDataPacketToBuffer(LiveDataPacket * pLiveData)
	{
		capnp::MallocMessageBuilder* message = new capnp::MallocMessageBuilder();
		rlbot::GameTickPacket::Builder packet = message->initRoot<rlbot::GameTickPacket>();

		populateBall(packet.initBall(), pLiveData->GameBall);
		auto players = packet.initPlayers(pLiveData->NumCars);
		for (int i = 0; i < players.size(); i++) {
			populatePlayer(players[i], pLiveData->GameCars[i]);
		}
		auto boosts = packet.initBoostPads(pLiveData->NumBoosts);
		for (int i = 0; i < boosts.size(); i++) {
			populateBoost(boosts[i], pLiveData->GameBoosts[i]);
		}
		populateGameInfo(packet.initGameInfo(), pLiveData->GameInfo);

		return toBuf(message);
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

}