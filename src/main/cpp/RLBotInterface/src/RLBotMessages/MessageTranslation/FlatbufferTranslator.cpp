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

		memcpy(structStr, widecstr, std::min(sizeof(PlayerConfiguration::name), (wcslen(widecstr) + 1) * sizeof(wchar_t))); // Copy over the string
		structStr[sizeof(PlayerConfiguration::name) / sizeof(wchar_t) - 1] = L'\0'; // Null terminate the string

	}

	void fillVector3Struct(const rlbot::flat::Vector3* vec, PyStruct::Vector3* structVec)
	{
		structVec->x = vec->x();
		structVec->y = vec->y();
		structVec->z = vec->z();
	}

	void fillRotatorStruct(const rlbot::flat::Rotator* rot, PyStruct::Rotator* structVec)
	{
		structVec->pitch = rot->pitch();
		structVec->yaw = rot->yaw();
		structVec->roll = rot->roll();
	}

	void fillBoxShapeStruct(const rlbot::flat::BoxShape* shape, BoxShape* structshape)
	{
		structshape->length = shape->length();
		structshape->width = shape->width();
		structshape->height = shape->height();
	}

	void fillSphereShapeStruct(const rlbot::flat::SphereShape* shape, SphereShape* structshape)
	{
		structshape->diameter = shape->diameter();
	}

	void fillCylinderShapeStruct(const rlbot::flat::CylinderShape* shape, CylinderShape* structshape)
	{
		structshape->diameter = shape->diameter();
		structshape->height = shape->height();
	}

	void fillCollisionShape(const rlbot::flat::BallInfo* ball, CollisionShape* shape)
	{
		switch (ball->shape_type())
		{
		case rlbot::flat::CollisionShape_BoxShape:
			shape->type = BoxType;
			fillBoxShapeStruct(ball->shape_as_BoxShape(), &shape->box);
			break;

		case rlbot::flat::CollisionShape_SphereShape:
			shape->type = SphereType;
			fillSphereShapeStruct(ball->shape_as_SphereShape(), &shape->sphere);
			break;

		case rlbot::flat::CollisionShape_CylinderShape:
			shape->type = CylinderType;
			fillCylinderShapeStruct(ball->shape_as_CylinderShape(), &shape->cylinder);
			break;
		}
	}

	void fillPhysicsStruct(const::rlbot::flat::Physics* physics, Physics* structPhysics)
	{
		fillVector3Struct(physics->location(), &structPhysics->location);
		if (physics->rotation())  // We don't always send a rotation value because it's useless info for the ball during predictions (which assume a round ball).
			fillRotatorStruct(physics->rotation(), &structPhysics->rotation);
		fillVector3Struct(physics->velocity(), &structPhysics->velocity);
		fillVector3Struct(physics->angularVelocity(), &structPhysics->angularVelocity);
	}

	void fillScoreStruct(const rlbot::flat::ScoreInfo* score, ScoreInfo* structScore)
	{
		structScore->assists = score->assists();
		structScore->demolitions = score->demolitions();
		structScore->goals = score->goals();
		structScore->ownGoals = score->ownGoals();
		structScore->saves = score->saves();
		structScore->score = score->score();
		structScore->shots = score->shots();
	}

	void fillPlayerStruct(const rlbot::flat::PlayerInfo* player, PlayerInfo* structPlayer)
	{
		fillPhysicsStruct(player->physics(), &structPlayer->physics);

		structPlayer->boost = player->boost();
		structPlayer->bot = player->isBot();
		structPlayer->demolished = player->isDemolished();
		structPlayer->doubleJumped = player->doubleJumped();
		structPlayer->jumped = player->jumped();
		fillStructName(player->name()->str(), structPlayer->name);
		structPlayer->onGround = player->hasWheelContact();
		fillScoreStruct(player->scoreInfo(), &structPlayer->score);
		structPlayer->superSonic = player->isSupersonic();
		structPlayer->team = player->team();
		fillBoxShapeStruct(player->hitbox(), &structPlayer->hitbox);
		fillVector3Struct(player->hitboxOffset(), &structPlayer->hitboxOffset);
		structPlayer->spawnId = player->spawnId();
	}

	void fillBoostStruct(const rlbot::flat::BoostPadState* boostState, BoostInfo* structBoost)
	{
		structBoost->active = boostState->isActive();
		structBoost->timer = boostState->timer();

		// Location is unavailable from BoostPadState. It will need to be added later from FieldInfo.
	}

	void fillTileStruct(const rlbot::flat::DropshotTile* tileInformation, TileInfo* structTile)
	{
		structTile->tileState = tileInformation->tileState();
	}

	void fillTouchStruct(const rlbot::flat::Touch* touch, Touch* structTouch)
	{
			fillStructName(touch->playerName()->str(), structTouch->playerName);
			fillVector3Struct(touch->location(), &structTouch->hitLocation);
			fillVector3Struct(touch->normal(), &structTouch->hitNormal);
			structTouch->timeSeconds = touch->gameSeconds();
			structTouch->team = touch->team();
			structTouch->playerIndex = touch->playerIndex();
	}

	void fillBallStruct(const rlbot::flat::BallInfo* ball, BallInfo* structBall)
	{
		fillPhysicsStruct(ball->physics(), &structBall->physics);

		if (flatbuffers::IsFieldPresent(ball, rlbot::flat::BallInfo::VT_LATESTTOUCH))
		{
			fillTouchStruct(ball->latestTouch(), &structBall->latestTouch);
		}
		else
		{
			fillStructName(std::string(""), structBall->latestTouch.playerName);
		}

		if (flatbuffers::IsFieldPresent(ball, rlbot::flat::BallInfo::VT_DROPSHOTINFO))
		{
			structBall->dropShotInfo.absorbedForce = ball->dropShotInfo()->absorbedForce();
			structBall->dropShotInfo.damageIndex = ball->dropShotInfo()->damageIndex();
			structBall->dropShotInfo.forceAccumRecent = ball->dropShotInfo()->forceAccumRecent();
		}

		fillCollisionShape(ball, &structBall->collisionShape);
	}

	void fillGameInfoStruct(const rlbot::flat::GameInfo* gameInfo, GameInfo* structGameInfo)
	{
		structGameInfo->kickoffPause = gameInfo->isKickoffPause();
		structGameInfo->gameTimeRemaining = gameInfo->gameTimeRemaining();
		structGameInfo->matchEnded = gameInfo->isMatchEnded();
		structGameInfo->overTime = gameInfo->isOvertime();
		structGameInfo->roundActive = gameInfo->isRoundActive();
		structGameInfo->timeSeconds = gameInfo->secondsElapsed();
		structGameInfo->unlimitedTime = gameInfo->isUnlimitedTime();
		structGameInfo->worldGravityZ = gameInfo->worldGravityZ();
		structGameInfo->gameSpeed = gameInfo->gameSpeed();
	}


	void fillTeamStruct(const rlbot::flat::TeamInfo* team, TeamInfo* structTeam)
	{
		structTeam->teamIndex = team->teamIndex();
		structTeam->score = team->score();
	}

	void translateToStruct(ByteBuffer flatbufferData, LiveDataPacket* packet)
	{
		if (flatbufferData.size == 0)
		{
			return; // Nothing to do.
		}

		static int prev_num_cars = 0;

		auto flatPacket = flatbuffers::GetRoot<rlbot::flat::GameTickPacket>(flatbufferData.ptr);

		auto players = flatPacket->players();
		if (players) {
			packet->numCars = players->size();
			int i = 0;
			for (; i < packet->numCars; i++) {
				fillPlayerStruct(players->Get(i), &packet->gameCars[i]);
			}

			// Zero out any slots that come after numCars. hitbox.height is chosen opportunistically as a value
			// that is non-zero if and only if there's data occupying the slot.
			for (; i < prev_num_cars; i++) {
				packet->gameCars[i] = PlayerInfo{ 0 };
			}

			prev_num_cars = packet->numCars;
		}

		auto boosts = flatPacket->boostPadStates();
		if (boosts) {
			packet->numBoosts = boosts->size();
			for (int i = 0; i < boosts->size(); i++) {
				fillBoostStruct(boosts->Get(i), &packet->gameBoosts[i]);
			}
		}

		auto tiles = flatPacket->tileInformation();
		if (tiles) {
			packet->numTiles = std::min((int) tiles->size(), CONST_MaxTiles);
			for (int i = 0; i < packet->numTiles; i++) {
				fillTileStruct(tiles->Get(i), &packet->gameTiles[i]);
			}
		}

		auto teams = flatPacket->teams();
		if (teams) {
			packet->numTeams = std::min((int) teams->size(), CONST_MaxTeams);
			for (int i = 0; i < packet->numTeams; i++) {
				fillTeamStruct(teams->Get(i), &packet->teams[i]);
			}
		}

		if (flatbuffers::IsFieldPresent(flatPacket, rlbot::flat::GameTickPacket::VT_BALL))
		{
			fillBallStruct(flatPacket->ball(), &packet->gameBall);
		}

		if (flatbuffers::IsFieldPresent(flatPacket, rlbot::flat::GameTickPacket::VT_GAMEINFO))
		{
			fillGameInfoStruct(flatPacket->gameInfo(), &packet->gameInfo);
		}
	}

	//void fillPlayerStruct(const rlbot::flat::PlayerInfo* player, PlayerInfo* structPlayer)
	void fillSliceStruct(const rlbot::flat::PredictionSlice* slice, Slice* structSlice)
	{
		fillPhysicsStruct(slice->physics(), &structSlice->physics);
		structSlice->gameSeconds = slice->gameSeconds();
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
			packet->numSlices = slices->size();
			for (int i = 0; i < slices->size(); i++) {
				fillSliceStruct(slices->Get(i), &packet->slice[i]);
			}
		}
	}

	void fillBoostPadStruct(const rlbot::flat::BoostPad* boostPad, BoostPad* structBoostPad)
	{
		fillVector3Struct(boostPad->location(), &structBoostPad->location);
		structBoostPad->fullBoost = boostPad->isFullBoost();
	}

	void fillGoalInfoStruct(const rlbot::flat::GoalInfo* goalInfo, GoalInfo* structGoalInfo)
	{
		structGoalInfo->teamNum = goalInfo->teamNum();
		fillVector3Struct(goalInfo->location(), &structGoalInfo->location);
		fillVector3Struct(goalInfo->direction(), &structGoalInfo->direction);
		structGoalInfo->width = goalInfo->width();
		structGoalInfo->height = goalInfo->height();
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
			packet->numBoosts = boostPads->size();
			for (int i = 0; i < boostPads->size(); i++)
			{
				fillBoostPadStruct(boostPads->Get(i), &packet->boostPads[i]);
			}
		}

		auto goals = fieldInfo->goals();
		if (goals)
		{
			packet->numGoals = goals->size();
			for (int i = 0; i < goals->size(); i++)
			{
				fillGoalInfoStruct(goals->Get(i), &packet->goals[i]);
			}
		}
	}

	void inputStructToFlatbuffer(flatbuffers::FlatBufferBuilder* builder, const PlayerInput& playerInput, int playerIndex)
	{
		auto controls = rlbot::flat::CreateControllerState(
			*builder,
			playerInput.throttle,
			playerInput.steer,
			playerInput.pitch,
			playerInput.yaw,
			playerInput.roll,
			playerInput.jump,
			playerInput.boost,
			playerInput.handbrake,
			playerInput.useItem);

		auto input = rlbot::flat::CreatePlayerInput(*builder, playerIndex, controls);

		builder->Finish(input);
	}

	void inputStructFromFlatbuffer(void* flatbuffer, PlayerInput& playerInput)
	{

		auto controllerState = flatbuffers::GetRoot<rlbot::flat::PlayerInput>(flatbuffer)->controllerState();

		playerInput.throttle = controllerState->throttle();
		playerInput.steer = controllerState->steer();
		playerInput.pitch = controllerState->pitch();
		playerInput.yaw = controllerState->yaw();
		playerInput.roll = controllerState->roll();
		playerInput.jump = controllerState->jump();
		playerInput.boost = controllerState->boost();
		playerInput.handbrake = controllerState->handbrake();
		playerInput.useItem = controllerState->useItem();
	}


	void fillQuaternionStruct(const rlbot::flat::Quaternion* quaternion, Quaternion* structQuaternion)
	{
		structQuaternion->x = quaternion->x();
		structQuaternion->y = quaternion->y();
		structQuaternion->z = quaternion->z();
		structQuaternion->w = quaternion->w();
	}

	void fillRBStateStruct(const rlbot::flat::RigidBodyState* rbState, RigidBodyState* structRBState)
	{
		structRBState->frame = rbState->frame();
		fillVector3Struct(rbState->location(), &structRBState->location);
		fillQuaternionStruct(rbState->rotation(), &structRBState->rotation);
		fillVector3Struct(rbState->velocity(), &structRBState->velocity);
		fillVector3Struct(rbState->angularVelocity(), &structRBState->angularVelocity);
	}

	void fillPlayerInputStruct(const rlbot::flat::ControllerState* controllerState, PlayerInput* structPlayerInput)
	{
		structPlayerInput->throttle = controllerState->throttle();
		structPlayerInput->steer = controllerState->steer();
		structPlayerInput->pitch = controllerState->pitch();
		structPlayerInput->yaw = controllerState->yaw();
		structPlayerInput->roll = controllerState->roll();
		structPlayerInput->jump = controllerState->jump();
		structPlayerInput->boost = controllerState->boost();
		structPlayerInput->handbrake = controllerState->handbrake();
		structPlayerInput->useItem = controllerState->useItem();
	}

	void fillPlayerPhysicsStruct(const rlbot::flat::PlayerRigidBodyState* playerState, PlayerRigidBodyState* structPlayerState)
	{
		fillRBStateStruct(playerState->state(), &structPlayerState->state);
		fillPlayerInputStruct(playerState->input(), &structPlayerState->input);
	}

	void fillBallPhysicsStruct(const rlbot::flat::BallRigidBodyState* ballState, BallRigidBodyState* structBallState)
	{
		fillRBStateStruct(ballState->state(), &structBallState->state);
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
			structTick->numPlayers = players->size();
			for (int i = 0; i < players->size(); i++) {
				fillPlayerPhysicsStruct(players->Get(i), &structTick->players[i]);
			}
		}

		fillBallPhysicsStruct(physicsTick->ball(), &structTick->ball);
	}

	void fillColor(const rlbot::flat::Color* color, Color* structColor)
	{
		structColor->a = color->a();
		structColor->r = color->r();
		structColor->g = color->g();
		structColor->b = color->b();
	}

	void fillPlayerLoadoutStruct(const rlbot::flat::PlayerLoadout* playerLoadout, PlayerConfiguration* structPlayerConfig)
	{
		if (playerLoadout)
		{
			structPlayerConfig->teamColorID = playerLoadout->teamColorId();
			structPlayerConfig->customColorID = playerLoadout->customColorId();
			structPlayerConfig->carID = playerLoadout->carId();
			structPlayerConfig->decalID = playerLoadout->decalId();
			structPlayerConfig->wheelsID = playerLoadout->wheelsId();
			structPlayerConfig->boostID = playerLoadout->boostId();
			structPlayerConfig->antennaID = playerLoadout->antennaId();
			structPlayerConfig->hatID = playerLoadout->hatId();
			structPlayerConfig->paintFinishID = playerLoadout->paintFinishId();
			structPlayerConfig->customFinishID = playerLoadout->customFinishId();
			structPlayerConfig->engineAudioID = playerLoadout->engineAudioId();
			structPlayerConfig->trailsID = playerLoadout->trailsId();
			structPlayerConfig->goalExplosionID = playerLoadout->goalExplosionId();
			if (playerLoadout->primaryColorLookup())
			{
				structPlayerConfig->useRgbLookup = true;
				fillColor(playerLoadout->primaryColorLookup(), &structPlayerConfig->primaryColorLookup);
			}

			if (playerLoadout->secondaryColorLookup())
			{
				structPlayerConfig->useRgbLookup = true;
				fillColor(playerLoadout->secondaryColorLookup(), &structPlayerConfig->secondaryColorLookup);
			}
		}

		auto playerPaint = playerLoadout->loadoutPaint();
		if (playerPaint)
		{
			structPlayerConfig->carPaintID = playerPaint->carPaintId();
			structPlayerConfig->decalPaintID = playerPaint->decalPaintId();
			structPlayerConfig->wheelsPaintID = playerPaint->wheelsPaintId();
			structPlayerConfig->boostPaintID = playerPaint->boostPaintId();
			structPlayerConfig->antennaPaintID = playerPaint->antennaPaintId();
			structPlayerConfig->hatPaintID = playerPaint->hatPaintId();
			structPlayerConfig->trailsPaintID = playerPaint->trailsPaintId();
			structPlayerConfig->goalExplosionPaintID = playerPaint->goalExplosionPaintId();
		}
	}

	void fillPlayerConfigurationStruct(const rlbot::flat::PlayerConfiguration* playerConfig, PlayerConfiguration* structPlayerConfig)
	{
		auto playerClass = playerConfig->variety_type();

		structPlayerConfig->bot =
			playerClass == rlbot::flat::PlayerClass::PlayerClass_RLBotPlayer ||
			playerClass == rlbot::flat::PlayerClass::PlayerClass_PsyonixBotPlayer;

		structPlayerConfig->rlbotControlled =
			playerClass == rlbot::flat::PlayerClass::PlayerClass_RLBotPlayer ||
			playerClass == rlbot::flat::PlayerClass::PlayerClass_PartyMemberBotPlayer;

		if (playerClass == rlbot::flat::PlayerClass::PlayerClass_PsyonixBotPlayer)
		{
			structPlayerConfig->botSkill = playerConfig->variety_as_PsyonixBotPlayer()->botSkill();
		}

		fillStructName(playerConfig->name()->str(), structPlayerConfig->name);
		structPlayerConfig->team = playerConfig->team();

		fillPlayerLoadoutStruct(playerConfig->loadout(), structPlayerConfig);

		structPlayerConfig->spawnId = playerConfig->spawnId();
	}

	void fillMutatorsStruct(const rlbot::flat::MutatorSettings* flatMutators, MutatorSettings* structMutators)
	{
		// We rely on the enums in the flatbuffer being in the exact same order as the ones in the struct, and therefore being numbered the same.
		structMutators->matchLength = static_cast<MatchLength>(flatMutators->matchLength());
		structMutators->maxScore = static_cast<MaxScore>(flatMutators->maxScore());
		structMutators->overtimeOptions = static_cast<OvertimeOption>(flatMutators->overtimeOption());
		structMutators->seriesLengthOptions = static_cast<SeriesLengthOption>(flatMutators->seriesLengthOption());
		structMutators->gameSpeedOptions = static_cast<GameSpeedOption>(flatMutators->gameSpeedOption());
		structMutators->ballMaxSpeedOptions = static_cast<BallMaxSpeedOption>(flatMutators->ballMaxSpeedOption());
		structMutators->ballTypeOptions = static_cast<BallTypeOption>(flatMutators->ballTypeOption());
		structMutators->ballWeightOptions = static_cast<BallWeightOption>(flatMutators->ballWeightOption());
		structMutators->ballSizeOptions = static_cast<BallSizeOption>(flatMutators->ballSizeOption());
		structMutators->ballBouncinessOptions = static_cast<BallBouncinessOption>(flatMutators->ballBouncinessOption());
		structMutators->boostOptions = static_cast<BoostOption>(flatMutators->boostOption());
		structMutators->rumbleOptions = static_cast<RumbleOption>(flatMutators->rumbleOption());
		structMutators->boostStrengthOptions = static_cast<BoostStrengthOption>(flatMutators->boostStrengthOption());
		structMutators->gravityOptions = static_cast<GravityOption>(flatMutators->gravityOption());
		structMutators->demolishOptions = static_cast<DemolishOption>(flatMutators->demolishOption());
		structMutators->respawnTimeOptions = static_cast<RespawnTimeOption>(flatMutators->respawnTimeOption());
	}

	void translateToMatchSettingsStruct(ByteBuffer flatbufferData, MatchSettings* matchSettings)
	{
		if (flatbufferData.size == 0)
		{
			return; // Nothing to do.
		}

		auto flatMatch = flatbuffers::GetRoot<rlbot::flat::MatchSettings>(flatbufferData.ptr);

		matchSettings->numPlayers = flatMatch->playerConfigurations()->size();
		for (int i = 0; i < matchSettings->numPlayers; i++) {
			fillPlayerConfigurationStruct(flatMatch->playerConfigurations()->Get(i), &matchSettings->playerConfiguration[i]);
		}

		// We rely on the enums in the flatbuffer being in the exact same order as the ones in the struct, and therefore being numbered the same.
		matchSettings->gameMap = static_cast<GameMap>(flatMatch->gameMap());
		matchSettings->gameMode = static_cast<GameMode>(flatMatch->gameMode());
		matchSettings->instantStart = flatMatch->instantStart();
		matchSettings->skipReplays = flatMatch->skipReplays();
		matchSettings->existingMatchBehavior = static_cast<ExistingMatchBehavior>(flatMatch->existingMatchBehavior());
		matchSettings->enableLockstep = flatMatch->enableLockstep();
		matchSettings->enableRendering = flatMatch->enableRendering();
		matchSettings->enableStateSetting = flatMatch->enableStateSetting();
		matchSettings->autoSaveReplay = flatMatch->autoSaveReplay();

		fillMutatorsStruct(flatMatch->mutatorSettings(), &matchSettings->mutatorSettings);
	}
}
