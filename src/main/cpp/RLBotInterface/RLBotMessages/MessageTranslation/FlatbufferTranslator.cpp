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

	int convertToURot(float radians)
	{
		return roundf(radians * 32768 / M_PI);
	}

	void fillRotatorStruct(const rlbot::flat::Rotator* rot, PyStruct::Rotator* structVec)
	{
		structVec->Pitch = convertToURot(rot->pitch());
		structVec->Yaw = convertToURot(rot->yaw());
		structVec->Roll = convertToURot(rot->roll());
	}

	void fillPhysicsStruct(const::rlbot::flat::Physics* physics, Physics* structPhysics)
	{
		fillVector3Struct(physics->location(), &structPhysics->Location);
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

	}

	void fillGameInfoStruct(const rlbot::flat::GameInfo* gameInfo, GameInfo* structGameInfo)
	{
		structGameInfo->BallHasBeenHit = !gameInfo->isKickoffPause();
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
		packet->NumCars = players->size();
		for (int i = 0; i < players->size(); i++) {
			fillPlayerStruct(players->Get(i), &packet->GameCars[i]);
		}

		auto boosts = flatPacket->boostPadStates();
		packet->NumBoosts = boosts->size();
		for (int i = 0; i < boosts->size(); i++) {
			fillBoostStruct(boosts->Get(i), &packet->GameBoosts[i]);
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
}
