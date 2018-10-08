#include "FlatbufferTranslator.hpp"
#include <rlbot_generated.h>
#include <algorithm>
#define _USE_MATH_DEFINES
#include <math.h>


namespace FlatbufferTranslator {

	void fillStructName(std::string str, wchar_t structStr[])
	{
		std::wstring widestr = std::wstring(str.begin(), str.end());
		const wchar_t* widecstr = widestr.c_str();

		memcpy(structStr, widecstr, min(sizeof(PlayerConfiguration::Name), (wcslen(widecstr) + 1) * sizeof(wchar_t))); // Copy over the string
		structStr[sizeof(PlayerConfiguration::Name) / sizeof(wchar_t) - 1] = L'\0'; // Null terminate the string

	}

	void fillVector3Struct(const rlbot::flat::Vector3* vec, PyStruct::Vector3* structVec)
	{
		structVec->X = vec->x();
		structVec->Y = vec->y();
		structVec->Z = vec->z();
	}

	void fillRotatorStruct(const rlbot::flat::Rotator* rot, PyStruct::Rotator* structVec)
	{
		structVec->Pitch = rot->pitch();
		structVec->Yaw = rot->yaw();
		structVec->Roll = rot->roll();
	}

	void fillPhysicsStruct(const::rlbot::flat::Physics* physics, Physics* structPhysics)
	{
		fillVector3Struct(physics->location(), &structPhysics->Location);
		if (physics->rotation())  // We don't always send a rotation value because it's useless info for the ball during predictions (which assume a round ball).
			fillRotatorStruct(physics->rotation(), &structPhysics->Rotation);
		fillVector3Struct(physics->velocity(), &structPhysics->Velocity);
		fillVector3Struct(physics->angularVelocity(), &structPhysics->AngularVelocity);
	}

	void fillScoreStruct(const rlbot::flat::ScoreInfo* score, ScoreInfo* structScore)
	{
		structScore->Assists = score->assists();
		structScore->Demolitions = score->demolitions();
		structScore->Goals = score->goals();
		structScore->OwnGoals = score->ownGoals();
		structScore->Saves = score->saves();
		structScore->Score = score->score();
		structScore->Shots = score->shots();
	}

	void fillPlayerStruct(const rlbot::flat::PlayerInfo* player, PlayerInfo* structPlayer)
	{
		fillPhysicsStruct(player->physics(), &structPlayer->Physics);

		structPlayer->Boost = player->boost();
		structPlayer->Bot = player->isBot();
		structPlayer->Demolished = player->isDemolished();
		structPlayer->DoubleJumped = player->doubleJumped();
		structPlayer->Jumped = player->jumped();
		fillStructName(player->name()->str(), structPlayer->Name);
		structPlayer->OnGround = player->hasWheelContact();
		fillScoreStruct(player->scoreInfo(), &structPlayer->Score);
		structPlayer->SuperSonic = player->isSupersonic();
		structPlayer->Team = player->team();
	}

	void fillBoostStruct(const rlbot::flat::BoostPadState* boostState, BoostInfo* structBoost)
	{
		structBoost->Active = boostState->isActive();
		structBoost->Timer = boostState->timer();

		// Location is unavailable from BoostPadState. It will need to be added later from FieldInfo.
	}

	void fillTileStruct(const rlbot::flat::DropshotTile* tileInformation, TileInfo* structTile)
	{
		structTile->tileState = tileInformation->tileState();
	}

	void fillTouchStruct(const rlbot::flat::Touch* touch, Touch* structTouch)
	{
			fillStructName(touch->playerName()->str(), structTouch->PlayerName);
			fillVector3Struct(touch->location(), &structTouch->HitLocation);
			fillVector3Struct(touch->normal(), &structTouch->HitNormal);
			structTouch->TimeSeconds = touch->gameSeconds();
	}

	void fillBallStruct(const rlbot::flat::BallInfo* ball, BallInfo* structBall)
	{
		fillPhysicsStruct(ball->physics(), &structBall->Physics);

		if (flatbuffers::IsFieldPresent(ball, rlbot::flat::BallInfo::VT_LATESTTOUCH))
		{
			fillTouchStruct(ball->latestTouch(), &structBall->LatestTouch);
		}
		else
		{
			fillStructName(std::string(""), structBall->LatestTouch.PlayerName);
		}

		if (flatbuffers::IsFieldPresent(ball, rlbot::flat::BallInfo::VT_DROPSHOTINFO))
		{
			structBall->DropShotInfo.AbsorbedForce = ball->dropShotInfo()->absorbedForce();
			structBall->DropShotInfo.DamageIndex = ball->dropShotInfo()->damageIndex();
			structBall->DropShotInfo.ForceAccumRecent = ball->dropShotInfo()->forceAccumRecent();
		}

	}

	void fillGameInfoStruct(const rlbot::flat::GameInfo* gameInfo, GameInfo* structGameInfo)
	{
		structGameInfo->KickoffPause = gameInfo->isKickoffPause();
		structGameInfo->GameTimeRemaining = gameInfo->gameTimeRemaining();
		structGameInfo->MatchEnded = gameInfo->isMatchEnded();
		structGameInfo->OverTime = gameInfo->isOvertime();
		structGameInfo->RoundActive = gameInfo->isRoundActive();
		structGameInfo->TimeSeconds = gameInfo->secondsElapsed();
		structGameInfo->UnlimitedTime = gameInfo->isUnlimitedTime();
	}

	void translateToStruct(ByteBuffer flatbufferData, LiveDataPacket* packet)
	{
		if (flatbufferData.size == 0)
		{
			return; // Nothing to do.
		}

		auto flatPacket = flatbuffers::GetRoot<rlbot::flat::GameTickPacket>(flatbufferData.ptr);

		auto players = flatPacket->players();
		if (players) {
			packet->NumCars = players->size();
			for (int i = 0; i < players->size(); i++) {
				fillPlayerStruct(players->Get(i), &packet->GameCars[i]);
			}
		}

		auto boosts = flatPacket->boostPadStates();
		if (boosts) {
			packet->NumBoosts = boosts->size();
			for (int i = 0; i < boosts->size(); i++) {
				fillBoostStruct(boosts->Get(i), &packet->GameBoosts[i]);
			}
		}

		auto tiles = flatPacket->tileInformation();
		if (tiles) {
			packet->NumTiles = tiles->size();
			for (int i = 0; i < tiles->size() && i < CONST_MaxTiles; i++) {
			fillTileStruct(tiles->Get(i), &packet->GameTiles[i]);
			}
		}

		if (flatbuffers::IsFieldPresent(flatPacket, rlbot::flat::GameTickPacket::VT_BALL))
		{
			fillBallStruct(flatPacket->ball(), &packet->GameBall);
		}

		if (flatbuffers::IsFieldPresent(flatPacket, rlbot::flat::GameTickPacket::VT_GAMEINFO))
		{
			fillGameInfoStruct(flatPacket->gameInfo(), &packet->GameInfo);
		}
	}

	//void fillPlayerStruct(const rlbot::flat::PlayerInfo* player, PlayerInfo* structPlayer)
	void fillSliceStruct(const rlbot::flat::PredictionSlice* slice, Slice* structSlice)
	{
		fillPhysicsStruct(slice->physics(), &structSlice->Physics);
		structSlice->GameSeconds = slice->gameSeconds();
	}

	void translateToPrediction(ByteBuffer flatbufferData, BallPredictionPacket* packet)
	{
		if (flatbufferData.size == 0)
		{
			return; // Nothing to do.
		}

		auto flatPacket = flatbuffers::GetRoot<rlbot::flat::BallPrediction>(flatbufferData.ptr);

		auto slices = flatPacket->slices();
		if (slices) {
			packet->NumSlices = slices->size();
			for (int i = 0; i < slices->size(); i++) {
				fillSliceStruct(slices->Get(i), &packet->Slice[i]);
			}
		}
	}

	void fillBoostPadStruct(const rlbot::flat::BoostPad* boostPad, BoostPad* structBoostPad)
	{
		fillVector3Struct(boostPad->location(), &structBoostPad->Location);
		structBoostPad->FullBoost = boostPad->isFullBoost();
	}

	void fillGoalInfoStruct(const rlbot::flat::GoalInfo* goalInfo, GoalInfo* structGoalInfo)
	{
		structGoalInfo->TeamNum = goalInfo->teamNum();
		fillVector3Struct(goalInfo->location(), &structGoalInfo->Location);
		fillVector3Struct(goalInfo->direction(), &structGoalInfo->Direction);
	}

	void translateToFieldInfoStruct(ByteBuffer flatbufferData, FieldInfo* packet)
	{
		if (flatbufferData.size == 0)
		{
			return; // Nothing to do. Return now to avoid a "Message did not contain a root pointer" error.
		}

		auto fieldInfo = flatbuffers::GetRoot<rlbot::flat::FieldInfo>(flatbufferData.ptr);

		auto boostPads = fieldInfo->boostPads();
		packet->NumBoosts = boostPads->size();
		for (int i = 0; i < boostPads->size(); i++)
		{
			fillBoostPadStruct(boostPads->Get(i), &packet->BoostPads[i]);
		}

		auto goals = fieldInfo->goals();
		packet->NumGoals = goals->size();
		for (int i = 0; i < goals->size(); i++)
		{
			fillGoalInfoStruct(goals->Get(i), &packet->Goals[i]);
		}
	}

	void inputStructToFlatbuffer(flatbuffers::FlatBufferBuilder* builder, const PlayerInput& playerInput, int playerIndex)
	{
		auto controls = rlbot::flat::CreateControllerState(
			*builder,
			playerInput.Throttle,
			playerInput.Steer,
			playerInput.Pitch,
			playerInput.Yaw,
			playerInput.Roll,
			playerInput.Jump,
			playerInput.Boost,
			playerInput.Handbrake);

		auto input = rlbot::flat::CreatePlayerInput(*builder, playerIndex, controls);

		builder->Finish(input);
	}


	void fillQuaternionStruct(const rlbot::flat::Quaternion* quaternion, Quaternion* structQuaternion)
	{
		structQuaternion->X = quaternion->x();
		structQuaternion->Y = quaternion->y();
		structQuaternion->Z = quaternion->z();
		structQuaternion->W = quaternion->w();
	}

	void fillRBStateStruct(const rlbot::flat::RigidBodyState* rbState, RigidBodyState* structRBState)
	{
		structRBState->Frame = rbState->frame();
		fillVector3Struct(rbState->location(), &structRBState->Location);
		fillQuaternionStruct(rbState->rotation(), &structRBState->Rotation);
		fillVector3Struct(rbState->velocity(), &structRBState->Velocity);
		fillVector3Struct(rbState->angularVelocity(), &structRBState->AngularVelocity);
	}

	void fillPlayerInputStruct(const rlbot::flat::ControllerState* controllerState, PlayerInput* structPlayerInput)
	{
		structPlayerInput->Throttle = controllerState->throttle();
		structPlayerInput->Steer = controllerState->steer();
		structPlayerInput->Pitch = controllerState->pitch();
		structPlayerInput->Yaw = controllerState->yaw();
		structPlayerInput->Roll = controllerState->roll();
		structPlayerInput->Jump = controllerState->jump();
		structPlayerInput->Boost = controllerState->boost();
		structPlayerInput->Handbrake = controllerState->handbrake();
	}

	void fillPlayerPhysicsStruct(const rlbot::flat::PlayerRigidBodyState* playerState, PlayerRigidBodyState* structPlayerState)
	{
		fillRBStateStruct(playerState->state(), &structPlayerState->State);
		fillPlayerInputStruct(playerState->input(), &structPlayerState->Input);
	}

	void fillBallPhysicsStruct(const rlbot::flat::BallRigidBodyState* ballState, BallRigidBodyState* structBallState)
	{
		fillRBStateStruct(ballState->state(), &structBallState->State);
	}

	void translateToRigidBodyStruct(ByteBuffer flatbufferData, RigidBodyTick* structTick)
	{
		if (flatbufferData.size == 0)
		{
			return; // Nothing to do.
		}

		auto physicsTick = flatbuffers::GetRoot<rlbot::flat::RigidBodyTick>(flatbufferData.ptr);

		auto players = physicsTick->players();
		if (players) {
			structTick->NumPlayers = players->size();
			for (int i = 0; i < players->size(); i++) {
				fillPlayerPhysicsStruct(players->Get(i), &structTick->Players[i]);
			}
		}

		fillBallPhysicsStruct(physicsTick->ball(), &structTick->Ball);
	}
}
