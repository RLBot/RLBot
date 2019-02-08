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
			structTouch->Team = touch->team();
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
		structGameInfo->WorldGravityZ = gameInfo->worldGravityZ();
		structGameInfo->GameSpeed = gameInfo->gameSpeed();
	}


	void fillTeamStruct(const rlbot::flat::TeamInfo* team, TeamInfo* structTeam)
	{
		structTeam->TeamIndex = team->teamIndex();
		structTeam->Score = team->score();
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
			packet->NumTiles = min(tiles->size(), CONST_MaxTiles);
			for (int i = 0; i < packet->NumTiles; i++) {
				fillTileStruct(tiles->Get(i), &packet->GameTiles[i]);
			}
		}

		auto teams = flatPacket->teams();
		if (teams) {
			packet->NumTeams = min(teams->size(), CONST_MaxTeams);
			for (int i = 0; i < packet->NumTeams; i++) {
				fillTeamStruct(teams->Get(i), &packet->Teams[i]);
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
		if (boostPads)
		{
			packet->NumBoosts = boostPads->size();
			for (int i = 0; i < boostPads->size(); i++)
			{
				fillBoostPadStruct(boostPads->Get(i), &packet->BoostPads[i]);
			}
		}
		
		auto goals = fieldInfo->goals();
		if (goals)
		{
			packet->NumGoals = goals->size();
			for (int i = 0; i < goals->size(); i++)
			{
				fillGoalInfoStruct(goals->Get(i), &packet->Goals[i]);
			}
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

	void inputStructFromFlatbuffer(void* flatbuffer, PlayerInput& playerInput)
	{

		auto controllerState = flatbuffers::GetRoot<rlbot::flat::PlayerInput>(flatbuffer)->controllerState();

		playerInput.Throttle = controllerState->throttle();
		playerInput.Steer = controllerState->steer();
		playerInput.Pitch = controllerState->pitch();
		playerInput.Yaw = controllerState->yaw();
		playerInput.Roll = controllerState->roll();
		playerInput.Jump = controllerState->jump();
		playerInput.Boost = controllerState->boost();
		playerInput.Handbrake = controllerState->handbrake();
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

	void fillPlayerLoadoutStruct(const rlbot::flat::PlayerLoadout* playerLoadout, PlayerConfiguration* structPlayerConfig)
	{
		structPlayerConfig->TeamColorID = playerLoadout->teamColorId();
		structPlayerConfig->CustomColorID = playerLoadout->customColorId();
		structPlayerConfig->CarID = playerLoadout->carId();
		structPlayerConfig->DecalID = playerLoadout->decalId();
		structPlayerConfig->WheelsID = playerLoadout->wheelsId();
		structPlayerConfig->BoostID = playerLoadout->boostId();
		structPlayerConfig->AntennaID = playerLoadout->antennaId();
		structPlayerConfig->HatID = playerLoadout->hatId();
		structPlayerConfig->PaintFinishID = playerLoadout->paintFinishId();
		structPlayerConfig->CustomFinishID = playerLoadout->customFinishId();
		structPlayerConfig->EngineAudioID = playerLoadout->engineAudioId();
		structPlayerConfig->TrailsID = playerLoadout->trailsId();
		structPlayerConfig->GoalExplosionID = playerLoadout->goalExplosionId();

		auto playerPaint = playerLoadout->loadoutPaint();
		structPlayerConfig->CarPaintID = playerPaint->carPaintId();
		structPlayerConfig->DecalPaintID = playerPaint->decalPaintId();
		structPlayerConfig->WheelsPaintID = playerPaint->wheelsPaintId();
		structPlayerConfig->BoostPaintID = playerPaint->boostPaintId();
		structPlayerConfig->AntennaPaintID = playerPaint->antennaPaintId();
		structPlayerConfig->HatPaintID = playerPaint->hatPaintId();
		structPlayerConfig->TrailsPaintID = playerPaint->trailsPaintId();
		structPlayerConfig->GoalExplosionPaintID = playerPaint->goalExplosionPaintId();
	}

	void fillPlayerConfigurationStruct(const rlbot::flat::PlayerConfiguration* playerConfig, PlayerConfiguration* structPlayerConfig)
	{
		auto playerClass = playerConfig->playerClass_type();

		structPlayerConfig->Bot = 
			playerClass == rlbot::flat::PlayerClass::PlayerClass_RLBotPlayer || 
			playerClass == rlbot::flat::PlayerClass::PlayerClass_PsyonixBotPlayer;

		structPlayerConfig->RLBotControlled = 
			playerClass == rlbot::flat::PlayerClass::PlayerClass_RLBotPlayer || 
			playerClass == rlbot::flat::PlayerClass::PlayerClass_PartyMemberBotPlayer;

		if (playerClass == rlbot::flat::PlayerClass::PlayerClass_PsyonixBotPlayer) 
		{
			structPlayerConfig->BotSkill = playerConfig->playerClass_as_PsyonixBotPlayer()->botSkill();
		}

		fillStructName(playerConfig->name()->str(), structPlayerConfig->Name);
		structPlayerConfig->Team = playerConfig->team();

		fillPlayerLoadoutStruct(playerConfig->loadout(), structPlayerConfig);
	}

	void fillMutatorsStruct(const rlbot::flat::MutatorSettings* flatMutators, MutatorSettings* structMutators)
	{
		// We rely on the enums in the flatbuffer being in the exact same order as the ones in the struct, and therefore being numbered the same.
		structMutators->MatchLength = static_cast<MatchLength>(flatMutators->matchLength());
		structMutators->MaxScore = static_cast<MaxScore>(flatMutators->maxScore());
		structMutators->OvertimeOptions = static_cast<OvertimeOption>(flatMutators->overtimeOption());
		structMutators->SeriesLengthOptions = static_cast<SeriesLengthOption>(flatMutators->seriesLengthOption());
		structMutators->GameSpeedOptions = static_cast<GameSpeedOption>(flatMutators->gameSpeedOption());
		structMutators->BallMaxSpeedOptions = static_cast<BallMaxSpeedOption>(flatMutators->ballMaxSpeedOption());
		structMutators->BallTypeOptions = static_cast<BallTypeOption>(flatMutators->ballTypeOption());
		structMutators->BallWeightOptions = static_cast<BallWeightOption>(flatMutators->ballWeightOption());
		structMutators->BallSizeOptions = static_cast<BallSizeOption>(flatMutators->ballSizeOption());
		structMutators->BallBouncinessOptions = static_cast<BallBouncinessOption>(flatMutators->ballBouncinessOption());
		structMutators->BoostOptions = static_cast<BoostOption>(flatMutators->boostOption());
		structMutators->RumbleOptions = static_cast<RumbleOption>(flatMutators->rumbleOption());
		structMutators->BoostStrengthOptions = static_cast<BoostStrengthOption>(flatMutators->boostStrengthOption());
		structMutators->GravityOptions = static_cast<GravityOption>(flatMutators->gravityOption());
		structMutators->DemolishOptions = static_cast<DemolishOption>(flatMutators->demolishOption());
		structMutators->RespawnTimeOptions = static_cast<RespawnTimeOption>(flatMutators->respawnTimeOption());
	}

	void translateToMatchSettingsStruct(ByteBuffer flatbufferData, MatchSettings* matchSettings)
	{
		if (flatbufferData.size == 0)
		{
			return; // Nothing to do.
		}

		auto flatMatch = flatbuffers::GetRoot<rlbot::flat::MatchSettings>(flatbufferData.ptr);

		matchSettings->NumPlayers = flatMatch->playerConfigurations()->size();
		for (int i = 0; i < matchSettings->NumPlayers; i++) {
			fillPlayerConfigurationStruct(flatMatch->playerConfigurations()->Get(i), &matchSettings->PlayerConfiguration[i]);
		}

		// We rely on the enums in the flatbuffer being in the exact same order as the ones in the struct, and therefore being numbered the same.
		matchSettings->GameMap = static_cast<GameMap>(flatMatch->gameMap());
		matchSettings->GameMode = static_cast<GameMode>(flatMatch->gameMode());
		matchSettings->InstantStart = flatMatch->instantStart();
		matchSettings->SkipReplays = flatMatch->skipReplays();
		
		fillMutatorsStruct(flatMatch->mutatorSettings(), &matchSettings->MutatorSettings);
	}
}
