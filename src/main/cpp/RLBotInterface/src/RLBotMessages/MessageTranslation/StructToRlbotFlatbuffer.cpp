#include "StructToRLBotFlatbuffer.hpp"


#define NOMINMAX
#include <algorithm>
#define _USE_MATH_DEFINES
#include <math.h>
#include <rlbot_generated.h>

#include <codecvt>
#include <cwchar>
#include <iostream>
#include <boost/locale/encoding_utf.hpp>



/*
Note: The code in this file looks goofy because flatbuffers requires us to construct things 'pre-order',
i.e. you have to fully create all the sub-objects before you start creating a parent object.

https://github.com/google/flatbuffers/blob/master/samples/sample_binary.cpp

*/
namespace StructToRLBotFlatbuffer
{
	flatbuffers::Offset<rlbot::flat::GameInfo> createGameInfo(flatbuffers::FlatBufferBuilder* builder, GameInfo gameInfo)
	{
		return rlbot::flat::CreateGameInfo(
			*builder,
			gameInfo.timeSeconds,
			gameInfo.gameTimeRemaining,
			gameInfo.overTime,
			gameInfo.unlimitedTime,
			gameInfo.roundActive,
			gameInfo.kickoffPause,
			gameInfo.matchEnded,
			gameInfo.worldGravityZ,
			gameInfo.gameSpeed);
	}

	rlbot::flat::Vector3 createVector3(PyStruct::Vector3 structVec)
	{
		return rlbot::flat::Vector3(structVec.x, structVec.y, structVec.z);
	}

	float convertURot(int rotation)
	{
		return rotation * M_PI / 32768;
	}

	rlbot::flat::Rotator createRotator(PyStruct::Rotator structRot)
	{
		return rlbot::flat::Rotator(
			convertURot(structRot.pitch),
			convertURot(structRot.yaw),
			convertURot(structRot.roll));
	}

	flatbuffers::Offset<rlbot::flat::BoxShape> createBoxShape(flatbuffers::FlatBufferBuilder & builder, BoxShape boxshape)
	{
		return rlbot::flat::CreateBoxShape(builder, boxshape.length, boxshape.width, boxshape.height);
	}

	flatbuffers::Offset<rlbot::flat::SphereShape> createSphereShape(flatbuffers::FlatBufferBuilder & builder, SphereShape sphereshape)
	{
		return rlbot::flat::CreateSphereShape(builder, sphereshape.diameter);
	}

	flatbuffers::Offset<rlbot::flat::CylinderShape> createCylinderShape(flatbuffers::FlatBufferBuilder & builder, CylinderShape cylindershape)
	{
		return rlbot::flat::CreateCylinderShape(builder, cylindershape.diameter, cylindershape.height);
	}

	flatbuffers::Offset<rlbot::flat::BoostPad> createBoostPad(flatbuffers::FlatBufferBuilder* builder, BoostPad boostPad)
	{
		auto location = createVector3(boostPad.location);
		return rlbot::flat::CreateBoostPad(*builder, &location, boostPad.fullBoost);
	}

	flatbuffers::Offset<rlbot::flat::BoostPadState> createBoostPadState(flatbuffers::FlatBufferBuilder* builder, BoostInfo gameBoost)
	{
		return rlbot::flat::CreateBoostPadState(*builder, gameBoost.active, gameBoost.timer);
	}

	flatbuffers::Offset<rlbot::flat::DropshotTile> createDropshotTile(flatbuffers::FlatBufferBuilder* builder, TileInfo dropshotTile)
	{
		rlbot::flat::TileState state;
		if (dropshotTile.tileState == 3)
			state = rlbot::flat::TileState::TileState_Open;
		else if (dropshotTile.tileState == 2)
			state = rlbot::flat::TileState::TileState_Damaged;

		state = rlbot::flat::TileState::TileState_Filled;

		return rlbot::flat::CreateDropshotTile(*builder, state);
	}

	bool FillFieldInfo(flatbuffers::FlatBufferBuilder* builder, FieldInfo fieldInfo)
	{
		std::vector<flatbuffers::Offset<rlbot::flat::BoostPad>> boostPads;

		for (int i = 0; i < fieldInfo.numBoosts; i++)
		{
			boostPads.push_back(createBoostPad(builder, fieldInfo.boostPads[i]));
		}

		std::vector<flatbuffers::Offset<rlbot::flat::GoalInfo>> goals;



		for (int i = 0; i < fieldInfo.numGoals; i++)
		{
			auto location = createVector3(fieldInfo.goals[i].location);
			auto direction = createVector3(fieldInfo.goals[i].direction);
			goals.push_back(rlbot::flat::CreateGoalInfo(*builder,
														fieldInfo.goals[i].teamNum,
														&location,
														&direction,
														fieldInfo.goals[i].width,
														fieldInfo.goals[i].height));
		}

		auto fieldInfoBuffer = rlbot::flat::CreateFieldInfo(*builder, builder->CreateVector(boostPads), builder->CreateVector(goals));
		builder->Finish(fieldInfoBuffer);

		return true;
	}

	flatbuffers::Offset<rlbot::flat::Physics> createPhysics(flatbuffers::FlatBufferBuilder* builder, Physics physics)
	{
		auto location = createVector3(physics.location);
		auto rotation = createRotator(physics.rotation);
		auto velocity = createVector3(physics.velocity);
		auto angular = createVector3(physics.angularVelocity);

		return rlbot::flat::CreatePhysics(*builder, &location, &rotation, &velocity, &angular);
	}

	std::string convertString(wchar_t* w)
	{
		std::wstring ws(w);
		return boost::locale::conv::utf_to_utf<char>(ws.c_str(), ws.c_str() + ws.size());
	}

	flatbuffers::Offset<rlbot::flat::PlayerInfo> createPlayerInfo(flatbuffers::FlatBufferBuilder* builder, PlayerInfo playerInfo)
	{
		rlbot::flat::ScoreInfoBuilder sib(*builder);

		sib.add_score(playerInfo.score.score);
		sib.add_goals(playerInfo.score.goals);
		sib.add_ownGoals(playerInfo.score.ownGoals);
		sib.add_assists(playerInfo.score.assists);
		sib.add_saves(playerInfo.score.saves);
		sib.add_shots(playerInfo.score.shots);
		sib.add_demolitions(playerInfo.score.demolitions);

		auto scoreInfo = sib.Finish();

		std::string name = convertString(playerInfo.name);
		auto flatName = builder->CreateString(name); // Must do this before PlayerInfoBuilder is started.
		auto physics = createPhysics(builder, playerInfo.physics);
		auto hitbox = createBoxShape(*builder, playerInfo.hitbox);
		auto hitboxOffset = createVector3(playerInfo.hitboxOffset);

		rlbot::flat::PlayerInfoBuilder pib(*builder);

		pib.add_scoreInfo(scoreInfo);
		pib.add_isBot(playerInfo.bot);
		pib.add_name(flatName);
		pib.add_isDemolished(playerInfo.demolished);
		pib.add_physics(physics);
		pib.add_hasWheelContact(playerInfo.onGround);
		pib.add_isSupersonic(playerInfo.superSonic);
		pib.add_jumped(playerInfo.jumped);
		pib.add_doubleJumped(playerInfo.doubleJumped);
		pib.add_team(playerInfo.team);
		pib.add_boost(playerInfo.boost);
		pib.add_hitbox(hitbox);
		pib.add_hitboxOffset(&hitboxOffset);
		pib.add_spawnId(playerInfo.spawnId);

		return pib.Finish();
	}

	flatbuffers::Offset<void> createCollisionShape(flatbuffers::FlatBufferBuilder & builder, CollisionShape collisionShape)
	{
		switch (collisionShape.type)
		{
		case BoxType:
			return createBoxShape(builder, collisionShape.box).Union();

		case SphereType:
			return createSphereShape(builder, collisionShape.sphere).Union();

		case CylinderType:
			return createCylinderShape(builder, collisionShape.cylinder).Union();
		}
	}

	rlbot::flat::CollisionShape createCollisionShapeType(CollisionShapeType collisionShapeType)
	{
		switch (collisionShapeType)
		{
		case BoxType:
			return rlbot::flat::CollisionShape_BoxShape;

		case SphereType:
			return rlbot::flat::CollisionShape_SphereShape;

		case CylinderType:
			return rlbot::flat::CollisionShape_CylinderShape;
		}
	}

	flatbuffers::Offset<rlbot::flat::BallInfo> createBallInfo(flatbuffers::FlatBufferBuilder* builder, BallInfo ballInfo)
	{
		bool hasTouch = ballInfo.latestTouch.timeSeconds > 0;
		flatbuffers::Offset<rlbot::flat::Touch> touchOffset;

		if (hasTouch)
		{
			std::string name = convertString(ballInfo.latestTouch.playerName);
			auto flatName = builder->CreateString(name); // Must do this before TouchBuilder is started

			auto touch = rlbot::flat::TouchBuilder(*builder);
			touch.add_playerName(flatName);
			touch.add_gameSeconds(ballInfo.latestTouch.timeSeconds);

			auto location = createVector3(ballInfo.latestTouch.hitLocation);
			touch.add_location(&location);

			auto normal = createVector3(ballInfo.latestTouch.hitNormal);
			touch.add_normal(&normal);

			touch.add_team(ballInfo.latestTouch.team);

			touch.add_playerIndex(ballInfo.latestTouch.playerIndex);

			touchOffset = touch.Finish();
		}

		auto physics = createPhysics(builder, ballInfo.physics);

		flatbuffers::Offset<rlbot::flat::DropShotBallInfo> dropShotBallOffset;

		rlbot::flat::DropShotBallInfoBuilder dbib(*builder);
		dbib.add_absorbedForce(ballInfo.dropShotInfo.absorbedForce);
		dbib.add_damageIndex(ballInfo.dropShotInfo.damageIndex);
		dbib.add_forceAccumRecent(ballInfo.dropShotInfo.forceAccumRecent);

		dropShotBallOffset = dbib.Finish();

		auto collisionshape = createCollisionShape(*builder, ballInfo.collisionShape);

		rlbot::flat::BallInfoBuilder bib(*builder);
		bib.add_physics(physics);

		if (hasTouch)
			bib.add_latestTouch(touchOffset);

		bib.add_dropShotInfo(dropShotBallOffset);
		bib.add_shape(collisionshape);
		bib.add_shape_type(createCollisionShapeType(ballInfo.collisionShape.type));

		return bib.Finish();
	}

	bool FillGameDataPacket(flatbuffers::FlatBufferBuilder* builder, LiveDataPacket liveDataPacket)
	{

		std::vector<flatbuffers::Offset<rlbot::flat::PlayerInfo>> players;
		flatbuffers::Offset<flatbuffers::Vector<flatbuffers::Offset<rlbot::flat::PlayerInfo>>> playersOffset;


		for (int i = 0; i < liveDataPacket.numCars; i++)
		{
			players.push_back(createPlayerInfo(builder, liveDataPacket.gameCars[i]));
		}

		playersOffset = builder->CreateVector(players);


		auto gameInfo = createGameInfo(builder, liveDataPacket.gameInfo);

		std::vector<flatbuffers::Offset<rlbot::flat::BoostPadState>> boosts;
		flatbuffers::Offset<flatbuffers::Vector<flatbuffers::Offset<rlbot::flat::BoostPadState>>> boostsOffset;


		for (int i = 0; i < liveDataPacket.numBoosts; i++)
		{
			boosts.push_back(createBoostPadState(builder, liveDataPacket.gameBoosts[i]));
		}

		boostsOffset = builder->CreateVector(boosts);

		std::vector<flatbuffers::Offset<rlbot::flat::DropshotTile>> tiles;
		flatbuffers::Offset<flatbuffers::Vector<flatbuffers::Offset<rlbot::flat::DropshotTile>>> tilesOffset;

		for (int i = 0; i < liveDataPacket.numTiles; i++)
		{
			tiles.push_back(createDropshotTile(builder, liveDataPacket.gameTiles[i]));
		}


		tilesOffset = builder->CreateVector(tiles);


		flatbuffers::Offset<rlbot::flat::BallInfo> ballOffset;

		ballOffset = createBallInfo(builder, liveDataPacket.gameBall);

		std::vector<flatbuffers::Offset<rlbot::flat::TeamInfo>> teamInfos;
		teamInfos.push_back(rlbot::flat::CreateTeamInfo(*builder, liveDataPacket.teams[0].teamIndex, liveDataPacket.teams[0].score));
		teamInfos.push_back(rlbot::flat::CreateTeamInfo(*builder, liveDataPacket.teams[1].teamIndex, liveDataPacket.teams[1].score));
		auto teamInfosOffset = builder->CreateVector(teamInfos);

		rlbot::flat::GameTickPacketBuilder gtb(*builder);
		gtb.add_gameInfo(gameInfo);

		gtb.add_players(playersOffset);
		gtb.add_boostPadStates(boostsOffset);
		gtb.add_tileInformation(tilesOffset);
		gtb.add_ball(ballOffset);
		gtb.add_teams(teamInfosOffset);

		builder->Finish(gtb.Finish());

		return true;
	}

	flatbuffers::Offset<rlbot::flat::Color> buildColor(flatbuffers::FlatBufferBuilder* builder, Color structColor)
	{
		return rlbot::flat::CreateColor(*builder, structColor.a, structColor.r, structColor.g, structColor.b);
	}

	flatbuffers::Offset<rlbot::flat::PlayerLoadout> buildPlayerLoadout(flatbuffers::FlatBufferBuilder* builder, PlayerConfiguration structPlayerConfig)
	{
		rlbot::flat::LoadoutPaintBuilder paintBuilder(*builder);
		paintBuilder.add_carPaintId(structPlayerConfig.carPaintID);
		paintBuilder.add_decalPaintId(structPlayerConfig.decalPaintID);
		paintBuilder.add_wheelsPaintId(structPlayerConfig.wheelsPaintID);
		paintBuilder.add_boostPaintId(structPlayerConfig.boostPaintID);
		paintBuilder.add_antennaPaintId(structPlayerConfig.antennaPaintID);
		paintBuilder.add_hatPaintId(structPlayerConfig.hatPaintID);
		paintBuilder.add_trailsPaintId(structPlayerConfig.trailsPaintID);
		paintBuilder.add_goalExplosionPaintId(structPlayerConfig.goalExplosionPaintID);
		auto paintOffset = paintBuilder.Finish();

		auto primaryColorOffset = buildColor(builder, structPlayerConfig.primaryColorLookup);
		auto secondaryColorOffset = buildColor(builder, structPlayerConfig.secondaryColorLookup);

		rlbot::flat::PlayerLoadoutBuilder loadoutBuilder(*builder);
		loadoutBuilder.add_teamColorId(structPlayerConfig.teamColorID);
		loadoutBuilder.add_customColorId(structPlayerConfig.customColorID);
		loadoutBuilder.add_carId(structPlayerConfig.carID);
		loadoutBuilder.add_decalId(structPlayerConfig.decalID);
		loadoutBuilder.add_wheelsId(structPlayerConfig.wheelsID);
		loadoutBuilder.add_boostId(structPlayerConfig.boostID);
		loadoutBuilder.add_antennaId(structPlayerConfig.antennaID);
		loadoutBuilder.add_hatId(structPlayerConfig.hatID);
		loadoutBuilder.add_paintFinishId(structPlayerConfig.paintFinishID);
		loadoutBuilder.add_customFinishId(structPlayerConfig.customFinishID);
		loadoutBuilder.add_engineAudioId(structPlayerConfig.engineAudioID);
		loadoutBuilder.add_trailsId(structPlayerConfig.trailsID);
		loadoutBuilder.add_goalExplosionId(structPlayerConfig.goalExplosionID);
		loadoutBuilder.add_loadoutPaint(paintOffset);
		if (structPlayerConfig.useRgbLookup)
		{
			loadoutBuilder.add_primaryColorLookup(primaryColorOffset);
			loadoutBuilder.add_secondaryColorLookup(secondaryColorOffset);
		}

		return loadoutBuilder.Finish();
	}

	flatbuffers::Offset<rlbot::flat::PlayerConfiguration> buildPlayerConfiguration(flatbuffers::FlatBufferBuilder* builder, PlayerConfiguration structPlayerConfig)
	{
		auto name = builder->CreateString(convertString(structPlayerConfig.name));
		auto loadout = buildPlayerLoadout(builder, structPlayerConfig);

		flatbuffers::Offset<void> player;
		rlbot::flat::PlayerClass variety;
		if (structPlayerConfig.bot)
		{
			if (structPlayerConfig.rlbotControlled)
			{
				variety = rlbot::flat::PlayerClass_RLBotPlayer;
				player = rlbot::flat::CreateRLBotPlayer(*builder).Union();
			}
			else
			{
				variety = rlbot::flat::PlayerClass_PsyonixBotPlayer;
				player = rlbot::flat::CreatePsyonixBotPlayer(*builder, structPlayerConfig.botSkill).Union();
			}
		}
		else
		{
			if (structPlayerConfig.rlbotControlled)
			{
				variety = rlbot::flat::PlayerClass_PartyMemberBotPlayer;
				player = rlbot::flat::CreatePartyMemberBotPlayer(*builder).Union();
			}
			else
			{
				variety = rlbot::flat::PlayerClass_HumanPlayer;
				player = rlbot::flat::CreateHumanPlayer(*builder).Union();
			}
		}


		rlbot::flat::PlayerConfigurationBuilder configBuilder(*builder);
		configBuilder.add_name(name);
		configBuilder.add_loadout(loadout);
		configBuilder.add_team(structPlayerConfig.team);
		configBuilder.add_variety(player);
		configBuilder.add_variety_type(variety);
		configBuilder.add_spawnId(structPlayerConfig.spawnId);

		return configBuilder.Finish();
	}

	flatbuffers::Offset<rlbot::flat::MutatorSettings> buildMutatorSettings(flatbuffers::FlatBufferBuilder* builder, MutatorSettings structMutators)
	{
		rlbot::flat::MutatorSettingsBuilder mutatorBuilder(*builder);
		// We rely on the enums in the flatbuffer being in the exact same order as the ones in the struct, and therefore being numbered the same.
		mutatorBuilder.add_matchLength(static_cast<rlbot::flat::MatchLength>(structMutators.matchLength));
		mutatorBuilder.add_maxScore(static_cast<rlbot::flat::MaxScore>(structMutators.maxScore));
		mutatorBuilder.add_overtimeOption(static_cast<rlbot::flat::OvertimeOption>(structMutators.overtimeOptions));
		mutatorBuilder.add_seriesLengthOption(static_cast<rlbot::flat::SeriesLengthOption>(structMutators.seriesLengthOptions));
		mutatorBuilder.add_gameSpeedOption(static_cast<rlbot::flat::GameSpeedOption>(structMutators.gameSpeedOptions));
		mutatorBuilder.add_ballMaxSpeedOption(static_cast<rlbot::flat::BallMaxSpeedOption>(structMutators.ballMaxSpeedOptions));
		mutatorBuilder.add_ballTypeOption(static_cast<rlbot::flat::BallTypeOption>(structMutators.ballTypeOptions));
		mutatorBuilder.add_ballWeightOption(static_cast<rlbot::flat::BallWeightOption>(structMutators.ballWeightOptions));
		mutatorBuilder.add_ballSizeOption(static_cast<rlbot::flat::BallSizeOption>(structMutators.ballSizeOptions));
		mutatorBuilder.add_ballBouncinessOption(static_cast<rlbot::flat::BallBouncinessOption>(structMutators.ballBouncinessOptions));
		mutatorBuilder.add_boostOption(static_cast<rlbot::flat::BoostOption>(structMutators.boostOptions));
		mutatorBuilder.add_rumbleOption(static_cast<rlbot::flat::RumbleOption>(structMutators.rumbleOptions));
		mutatorBuilder.add_boostStrengthOption(static_cast<rlbot::flat::BoostStrengthOption>(structMutators.boostStrengthOptions));
		mutatorBuilder.add_gravityOption(static_cast<rlbot::flat::GravityOption>(structMutators.gravityOptions));
		mutatorBuilder.add_demolishOption(static_cast<rlbot::flat::DemolishOption>(structMutators.demolishOptions));
		mutatorBuilder.add_respawnTimeOption(static_cast<rlbot::flat::RespawnTimeOption>(structMutators.respawnTimeOptions));
		return mutatorBuilder.Finish();
	}


	bool BuildStartMatchMessage(flatbuffers::FlatBufferBuilder* builder, MatchSettings matchSettings)
	{
		std::vector<flatbuffers::Offset<rlbot::flat::PlayerConfiguration>> playerConfigOffsets;

		for (int i = 0; i < matchSettings.numPlayers; i++)
		{
			playerConfigOffsets.push_back(buildPlayerConfiguration(builder, matchSettings.playerConfiguration[i]));
		}

		auto matchSettingsFlat = rlbot::flat::CreateMatchSettings(
			*builder,
			builder->CreateVector(playerConfigOffsets),
			static_cast<rlbot::flat::GameMode>(matchSettings.gameMode),
			static_cast<rlbot::flat::GameMap>(matchSettings.gameMap),
			matchSettings.skipReplays,
			matchSettings.instantStart,
			buildMutatorSettings(builder, matchSettings.mutatorSettings),
			static_cast<rlbot::flat::ExistingMatchBehavior>(matchSettings.existingMatchBehavior),
			matchSettings.enableLockstep);

		builder->Finish(matchSettingsFlat);

		return true;
	}

	rlbot::flat::Quaternion createQuaternion(Quaternion structQuaternion)
	{
		return rlbot::flat::Quaternion(structQuaternion.x, structQuaternion.y, structQuaternion.z, structQuaternion.w);
	}

	flatbuffers::Offset<rlbot::flat::RigidBodyState> createRigidBodyState(flatbuffers::FlatBufferBuilder* builder, RigidBodyState state)
	{
		auto location = createVector3(state.location);
		auto rotation = createQuaternion(state.rotation);
		auto velocity = createVector3(state.velocity);
		auto angular = createVector3(state.angularVelocity);

		return rlbot::flat::CreateRigidBodyState(*builder, state.frame, &location, &rotation, &velocity, &angular);
	}

	flatbuffers::Offset<rlbot::flat::ControllerState> createControllerState(flatbuffers::FlatBufferBuilder* builder, PlayerInput structPlayerInput)
	{
		return rlbot::flat::CreateControllerState(*builder,
			structPlayerInput.throttle,
			structPlayerInput.steer,
			structPlayerInput.pitch,
			structPlayerInput.yaw,
			structPlayerInput.roll,
			structPlayerInput.jump,
			structPlayerInput.boost,
			structPlayerInput.handbrake,
			structPlayerInput.useItem);
	}

	flatbuffers::Offset<rlbot::flat::PlayerRigidBodyState> createPlayerRigid(flatbuffers::FlatBufferBuilder* builder, PlayerRigidBodyState stateStruct)
	{
		auto state = createRigidBodyState(builder, stateStruct.state);
		auto input = createControllerState(builder, stateStruct.input);

		return rlbot::flat::CreatePlayerRigidBodyState(*builder, state, input);

	}

	flatbuffers::Offset<rlbot::flat::BallRigidBodyState> createBallRigidBody(flatbuffers::FlatBufferBuilder* builder, BallRigidBodyState structBallState)
	{
		return rlbot::flat::CreateBallRigidBodyState(*builder, createRigidBodyState(builder, structBallState.state));
	}

	bool FillRigidBody(flatbuffers::FlatBufferBuilder* builder, RigidBodyTick rigidBodyTick)
	{
		std::vector<flatbuffers::Offset<rlbot::flat::PlayerRigidBodyState>> players;
		flatbuffers::Offset<flatbuffers::Vector<flatbuffers::Offset<rlbot::flat::PlayerRigidBodyState>>> playersOffset;


		for (int i = 0; i < rigidBodyTick.numPlayers; i++)
		{
			players.push_back(createPlayerRigid(builder, rigidBodyTick.players[i]));
		}

		playersOffset = builder->CreateVector(players);

		flatbuffers::Offset<rlbot::flat::BallRigidBodyState> ballOffset;

		ballOffset = createBallRigidBody(builder, rigidBodyTick.ball);

		auto tickOffset = rlbot::flat::CreateRigidBodyTick(*builder, ballOffset, playersOffset);

		builder->Finish(tickOffset);

		return true;
	}
}
