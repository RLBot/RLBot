#ifdef ENABLE_PROTO

#include "ProtoConversions.hpp"

#define _USE_MATH_DEFINES
#include <math.h>

namespace ProtoConversions {

	std::string convertString(wchar_t* w) {
		std::wstring ws(w);
		std::string str(ws.begin(), ws.end());
		return str;
	}

	rlbot::api::ScoreInfo* convertScoreInfo(ScoreInfo si) {
		auto protoScore = new rlbot::api::ScoreInfo();
		protoScore->set_assists(si.Assists);
		protoScore->set_demolitions(si.Demolitions);
		protoScore->set_goals(si.Goals);
		protoScore->set_own_goals(si.OwnGoals);
		protoScore->set_saves(si.Saves);
		protoScore->set_score(si.Score);
		protoScore->set_shots(si.Shots);

		return protoScore;
	}

	float convertURot(int rotation) {
		return rotation * M_PI / 32768;
	}

	rlbot::api::Rotator* convertRotation(Rotator rot) {
		auto protoRot = new rlbot::api::Rotator();
		protoRot->set_pitch(convertURot(rot.Pitch));
		protoRot->set_yaw(convertURot(rot.Yaw));
		protoRot->set_roll(convertURot(rot.Roll));

		return protoRot;
	}

	rlbot::api::Vector3* convertVector(Vector3 vec) {
		auto protoVec = new rlbot::api::Vector3();
		protoVec->set_x(vec.X);
		protoVec->set_y(vec.Y);
		protoVec->set_z(vec.Z);

		return protoVec;
	}

	void setupPlayerInfo(PlayerInfo car, rlbot::api::PlayerInfo* protoCar) {
		protoCar->set_name(convertString(car.Name));
		protoCar->set_team(car.Team);
		protoCar->set_boost(car.Boost);
		protoCar->set_allocated_rotation(convertRotation(car.Rotation));
		protoCar->set_allocated_angular_velocity(convertVector(car.AngularVelocity));
		protoCar->set_allocated_location(convertVector(car.Location));
		protoCar->set_allocated_score_info(convertScoreInfo(car.Score));
		protoCar->set_allocated_velocity(convertVector(car.Velocity));
		protoCar->set_jumped(car.Jumped);
		protoCar->set_double_jumped(car.DoubleJumped);
		protoCar->set_is_bot(car.Bot);
		protoCar->set_is_demolished(car.Demolished);
		protoCar->set_is_midair(!car.OnGround);
		protoCar->set_is_supersonic(car.SuperSonic);
	}

	void setupBoostInfo(BoostInfo boost, rlbot::api::BoostInfo* protoBoost) {
		protoBoost->set_allocated_location(convertVector(boost.Location));
		protoBoost->set_is_active(boost.Active);
		protoBoost->set_timer(boost.Timer);
	}

	rlbot::api::Touch* convertTouch(Touch touch) {
		auto protoTouch = new rlbot::api::Touch();
		protoTouch->set_allocated_location(convertVector(touch.HitLocation));
		protoTouch->set_allocated_normal(convertVector(touch.HitNormal));
		protoTouch->set_player_name(convertString(touch.PlayerName));
		protoTouch->set_game_seconds(touch.TimeSeconds);

		return protoTouch;
	}

	rlbot::api::BallInfo* convertBall(BallInfo ball) {
		auto protoBall = new rlbot::api::BallInfo();
		protoBall->set_allocated_location(convertVector(ball.Location));
		protoBall->set_allocated_velocity(convertVector(ball.Velocity));
		protoBall->set_allocated_acceleration(convertVector(ball.Acceleration));
		protoBall->set_allocated_rotation(convertRotation(ball.Rotation));
		protoBall->set_allocated_angular_velocity(convertVector(ball.AngularVelocity));
		protoBall->set_allocated_latest_touch(convertTouch(ball.LatestTouch));

		return protoBall;
	}

	rlbot::api::GameInfo* convertGameInfo(GameInfo info) {
		auto protoInfo = new rlbot::api::GameInfo();
		protoInfo->set_game_time_remaining(info.GameTimeRemaining);
		protoInfo->set_is_kickoff_pause(!info.BallHasBeenHit);
		protoInfo->set_is_match_ended(info.MatchEnded);
		protoInfo->set_is_overtime(info.OverTime);
		protoInfo->set_is_round_active(info.RoundActive);
		protoInfo->set_is_unlimited_time(info.UnlimitedTime);
		protoInfo->set_seconds_elapsed(info.TimeSeconds);

		return protoInfo;
	}

	rlbot::api::GameTickPacket* convert(LiveDataPacket * pLiveData)
	{
		auto packet = new rlbot::api::GameTickPacket();

		for (int i = 0; i < pLiveData->NumCars; i++) {
			PlayerInfo car = pLiveData->GameCars[i];
			rlbot::api::PlayerInfo* protoCar = packet->add_players();
			setupPlayerInfo(car, protoCar);
		}

		for (int i = 0; i < pLiveData->NumBoosts; i++) {
			BoostInfo boost = pLiveData->GameBoosts[i];
			rlbot::api::BoostInfo* protoBoost = packet->add_boost_pads();
			setupBoostInfo(boost, protoBoost);
		}

		packet->set_player_index(-1);
		packet->set_allocated_ball(convertBall(pLiveData->GameBall));
		packet->set_allocated_game_info(convertGameInfo(pLiveData->GameInfo));

		return packet;
	}

	RLBotCoreStatus convert(rlbot::api::GameTickPacket* protoResult, LiveDataPacket* pLiveData)
	{
		// This should copy over only the data that has been set from protoResult to pLiveData
		return RLBotCoreStatus::Success;
	}

	PlayerInput* convert(rlbot::api::ControllerState* protoResult)
	{
		PlayerInput* playerInput = new PlayerInput();
		playerInput->Boost = protoResult->boost();
		playerInput->Handbrake = protoResult->handbrake();
		playerInput->Jump = protoResult->jump();
		playerInput->Pitch = protoResult->pitch();
		playerInput->Roll = protoResult->roll();
		playerInput->Steer = protoResult->steer();
		playerInput->Throttle = protoResult->throttle();
		playerInput->Yaw = protoResult->yaw();
		
		return playerInput;
	}
}

#endif