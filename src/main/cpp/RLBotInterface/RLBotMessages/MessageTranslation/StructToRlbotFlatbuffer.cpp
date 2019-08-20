#include "StructToRLBotFlatbuffer.hpp"


#define NOMINMAX
#include <algorithm>
#define _USE_MATH_DEFINES
#include <math.h>
#include <rlbot_generated.h>

#include <iostream>

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
			gameInfo.TimeSeconds,
			gameInfo.GameTimeRemaining,
			gameInfo.OverTime,
			gameInfo.UnlimitedTime,
			gameInfo.RoundActive,
			gameInfo.KickoffPause,
			gameInfo.MatchEnded,
			gameInfo.WorldGravityZ,
			gameInfo.GameSpeed);
	}

	rlbot::flat::Vector3 createVector3(PyStruct::Vector3 structVec)
	{
		return rlbot::flat::Vector3(structVec.X, structVec.Y, structVec.Z);
	}

	float convertURot(int rotation)
	{
		return rotation * M_PI / 32768;
	}

	rlbot::flat::Rotator createRotator(PyStruct::Rotator structRot)
	{
		return rlbot::flat::Rotator(
			convertURot(structRot.Pitch),
			convertURot(structRot.Yaw),
			convertURot(structRot.Roll));
	}

	flatbuffers::Offset<rlbot::flat::BoostPad> createBoostPad(flatbuffers::FlatBufferBuilder* builder, BoostPad boostPad)
	{
		auto location = createVector3(boostPad.Location);
		return rlbot::flat::CreateBoostPad(*builder, &location, boostPad.FullBoost);
	}

	flatbuffers::Offset<rlbot::flat::BoostPadState> createBoostPadState(flatbuffers::FlatBufferBuilder* builder, BoostInfo gameBoost)
	{
		return rlbot::flat::CreateBoostPadState(*builder, gameBoost.Active, gameBoost.Timer);
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

		for (int i = 0; i < fieldInfo.NumBoosts; i++)
		{
			boostPads.push_back(createBoostPad(builder, fieldInfo.BoostPads[i]));
		}

		std::vector<flatbuffers::Offset<rlbot::flat::GoalInfo>> goals;
		


		for (int i = 0; i < fieldInfo.NumGoals; i++)
		{
			auto location = createVector3(fieldInfo.Goals[i].Location);
			auto direction = createVector3(fieldInfo.Goals[i].Direction);
			goals.push_back(rlbot::flat::CreateGoalInfo(*builder, fieldInfo.Goals[i].TeamNum, &location, &direction));
		}

		auto fieldInfoBuffer = rlbot::flat::CreateFieldInfo(*builder, builder->CreateVector(boostPads), builder->CreateVector(goals));
		builder->Finish(fieldInfoBuffer);

		return true;
	}

	flatbuffers::Offset<rlbot::flat::Physics> createPhysics(flatbuffers::FlatBufferBuilder* builder, Physics physics)
	{
		auto location = createVector3(physics.Location);
		auto rotation = createRotator(physics.Rotation);
		auto velocity = createVector3(physics.Velocity);
		auto angular = createVector3(physics.AngularVelocity);

		return rlbot::flat::CreatePhysics(*builder, &location, &rotation, &velocity, &angular);
	}

	std::string convertString(wchar_t* w)
	{
		std::wstring ws(w);
		std::string str(ws.begin(), ws.end());
		return str;
	}

	flatbuffers::Offset<rlbot::flat::PlayerInfo> createPlayerInfo(flatbuffers::FlatBufferBuilder* builder, PlayerInfo playerInfo)
	{
		rlbot::flat::ScoreInfoBuilder sib(*builder);

		sib.add_score(playerInfo.Score.Score);
		sib.add_goals(playerInfo.Score.Goals);
		sib.add_ownGoals(playerInfo.Score.OwnGoals);
		sib.add_assists(playerInfo.Score.Assists);
		sib.add_saves(playerInfo.Score.Saves);
		sib.add_shots(playerInfo.Score.Shots);
		sib.add_demolitions(playerInfo.Score.Demolitions);

		auto scoreInfo = sib.Finish();

		std::string name = convertString(playerInfo.Name);
		auto flatName = builder->CreateString(name); // Must do this before PlayerInfoBuilder is started.
		auto physics = createPhysics(builder, playerInfo.Physics);

		rlbot::flat::PlayerInfoBuilder pib(*builder);

		pib.add_scoreInfo(scoreInfo);
		pib.add_isBot(playerInfo.Bot);
		pib.add_name(flatName);
		pib.add_isDemolished(playerInfo.Demolished);
		pib.add_physics(physics);
		pib.add_hasWheelContact(playerInfo.OnGround);
		pib.add_isSupersonic(playerInfo.SuperSonic);
		pib.add_jumped(playerInfo.Jumped);
		pib.add_doubleJumped(playerInfo.DoubleJumped);
		pib.add_team(playerInfo.Team);
		pib.add_boost(playerInfo.Boost);

		return pib.Finish();
	}

	flatbuffers::Offset<rlbot::flat::BallInfo> createBallInfo(flatbuffers::FlatBufferBuilder* builder, BallInfo ballInfo)
	{
		bool hasTouch = ballInfo.LatestTouch.TimeSeconds > 0;
		flatbuffers::Offset<rlbot::flat::Touch> touchOffset;

		if (hasTouch)
		{
			std::string name = convertString(ballInfo.LatestTouch.PlayerName);
			auto flatName = builder->CreateString(name); // Must do this before TouchBuilder is started

			auto touch = rlbot::flat::TouchBuilder(*builder);
			touch.add_playerName(flatName);
			touch.add_gameSeconds(ballInfo.LatestTouch.TimeSeconds);

			auto location = createVector3(ballInfo.LatestTouch.HitLocation);
			touch.add_location(&location);

			auto normal = createVector3(ballInfo.LatestTouch.HitNormal);
			touch.add_normal(&normal);

			touch.add_team(ballInfo.LatestTouch.Team);

			touch.add_playerIndex(ballInfo.LatestTouch.PlayerIndex);

			touchOffset = touch.Finish();
		}

		auto physics = createPhysics(builder, ballInfo.Physics);

		flatbuffers::Offset<rlbot::flat::DropShotBallInfo> dropShotBallOffset;

		rlbot::flat::DropShotBallInfoBuilder dbib(*builder);
		dbib.add_absorbedForce(ballInfo.DropShotInfo.AbsorbedForce);
		dbib.add_damageIndex(ballInfo.DropShotInfo.DamageIndex);
		dbib.add_forceAccumRecent(ballInfo.DropShotInfo.ForceAccumRecent);

		dropShotBallOffset = dbib.Finish();
		

		rlbot::flat::BallInfoBuilder bib(*builder);
		bib.add_physics(physics);

		if (hasTouch)
			bib.add_latestTouch(touchOffset);


		bib.add_dropShotInfo(dropShotBallOffset);

		return bib.Finish();
	}

	bool FillGameDataPacket(flatbuffers::FlatBufferBuilder* builder, LiveDataPacket liveDataPacket)
	{

		std::vector<flatbuffers::Offset<rlbot::flat::PlayerInfo>> players;
		flatbuffers::Offset<flatbuffers::Vector<flatbuffers::Offset<rlbot::flat::PlayerInfo>>> playersOffset;


		for (int i = 0; i < liveDataPacket.NumCars; i++)
		{
			players.push_back(createPlayerInfo(builder, liveDataPacket.GameCars[i]));	
		}

		playersOffset = builder->CreateVector(players);
		

		auto gameInfo = createGameInfo(builder, liveDataPacket.GameInfo);

		std::vector<flatbuffers::Offset<rlbot::flat::BoostPadState>> boosts;
		flatbuffers::Offset<flatbuffers::Vector<flatbuffers::Offset<rlbot::flat::BoostPadState>>> boostsOffset;


		for (int i = 0; i < liveDataPacket.NumBoosts; i++)
		{
			boosts.push_back(createBoostPadState(builder, liveDataPacket.GameBoosts[i]));
		}

		boostsOffset = builder->CreateVector(boosts);
		
		std::vector<flatbuffers::Offset<rlbot::flat::DropshotTile>> tiles;
		flatbuffers::Offset<flatbuffers::Vector<flatbuffers::Offset<rlbot::flat::DropshotTile>>> tilesOffset;
		
		for (int i = 0; i < liveDataPacket.NumTiles; i++)
		{
			tiles.push_back(createDropshotTile(builder, liveDataPacket.GameTiles[i]));
		}


		tilesOffset = builder->CreateVector(tiles);
		

		flatbuffers::Offset<rlbot::flat::BallInfo> ballOffset;

		ballOffset = createBallInfo(builder, liveDataPacket.GameBall);

		std::vector<flatbuffers::Offset<rlbot::flat::TeamInfo>> teamInfos;
		teamInfos.push_back(rlbot::flat::CreateTeamInfo(*builder, liveDataPacket.Teams[0].TeamIndex, liveDataPacket.Teams[0].Score));
		teamInfos.push_back(rlbot::flat::CreateTeamInfo(*builder, liveDataPacket.Teams[1].TeamIndex, liveDataPacket.Teams[1].Score));
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

	bool FillFieldInfoPacket(flatbuffers::FlatBufferBuilder* builder, FieldInfo fieldInfoPacket)
	{
		bool filled;

		std::vector<flatbuffers::Offset<rlbot::flat::BoostPad>> boostPads;

		for (int i = 0; i < fieldInfoPacket.NumBoosts; i++)
		{
			boostPads.push_back(createBoostPad(builder, fieldInfoPacket.BoostPads[i]));
		}

		std::vector<flatbuffers::Offset<rlbot::flat::GoalInfo>> goals;

		for (int i = 0; i < fieldInfoPacket.NumGoals; i++)
		{
			GoalInfo goal = fieldInfoPacket.Goals[i];
			auto location = createVector3(goal.Location);
			auto direction = createVector3(goal.Direction);
			goals.push_back(rlbot::flat::CreateGoalInfo(*builder, goal.TeamNum, &location, &direction));

			filled = true;
		}

		auto fieldInfo = rlbot::flat::CreateFieldInfo(*builder, builder->CreateVector(boostPads), builder->CreateVector(goals));
		builder->Finish(fieldInfo);

		return filled;
	}

	flatbuffers::Offset<rlbot::flat::PlayerLoadout> buildPlayerLoadout(flatbuffers::FlatBufferBuilder* builder, PlayerConfiguration structPlayerConfig)
	{
		rlbot::flat::LoadoutPaintBuilder paintBuilder(*builder);
		paintBuilder.add_carPaintId(structPlayerConfig.CarPaintID);
		paintBuilder.add_decalPaintId(structPlayerConfig.DecalPaintID);
		paintBuilder.add_wheelsPaintId(structPlayerConfig.WheelsPaintID);
		paintBuilder.add_boostPaintId(structPlayerConfig.BoostPaintID);
		paintBuilder.add_antennaPaintId(structPlayerConfig.AntennaPaintID);
		paintBuilder.add_hatPaintId(structPlayerConfig.HatPaintID);
		paintBuilder.add_trailsPaintId(structPlayerConfig.TrailsPaintID);
		paintBuilder.add_goalExplosionPaintId(structPlayerConfig.GoalExplosionPaintID);
		auto paintOffset = paintBuilder.Finish();

		rlbot::flat::PlayerLoadoutBuilder loadoutBuilder(*builder);
		loadoutBuilder.add_teamColorId(structPlayerConfig.TeamColorID);
		loadoutBuilder.add_customColorId(structPlayerConfig.CustomColorID);
		loadoutBuilder.add_carId(structPlayerConfig.CarID);
		loadoutBuilder.add_decalId(structPlayerConfig.DecalID);
		loadoutBuilder.add_wheelsId(structPlayerConfig.WheelsID);
		loadoutBuilder.add_boostId(structPlayerConfig.BoostID);
		loadoutBuilder.add_antennaId(structPlayerConfig.AntennaID);
		loadoutBuilder.add_hatId(structPlayerConfig.HatID);
		loadoutBuilder.add_paintFinishId(structPlayerConfig.PaintFinishID);
		loadoutBuilder.add_customFinishId(structPlayerConfig.CustomFinishID);
		loadoutBuilder.add_engineAudioId(structPlayerConfig.EngineAudioID);
		loadoutBuilder.add_trailsId(structPlayerConfig.TrailsID);
		loadoutBuilder.add_goalExplosionId(structPlayerConfig.GoalExplosionID);
		loadoutBuilder.add_loadoutPaint(paintOffset);
		return loadoutBuilder.Finish();
	}

	flatbuffers::Offset<rlbot::flat::PlayerConfiguration> buildPlayerConfiguration(flatbuffers::FlatBufferBuilder* builder, PlayerConfiguration structPlayerConfig)
	{
		auto name = builder->CreateString(convertString(structPlayerConfig.Name));
		auto loadout = buildPlayerLoadout(builder, structPlayerConfig);

		flatbuffers::Offset<void> player;
		rlbot::flat::PlayerClass variety;
		if (structPlayerConfig.Bot)
		{
			if (structPlayerConfig.RLBotControlled)
			{
				variety = rlbot::flat::PlayerClass_RLBotPlayer;
				player = rlbot::flat::CreateRLBotPlayer(*builder).Union();
			}
			else
			{
				variety = rlbot::flat::PlayerClass_PsyonixBotPlayer;
				player = rlbot::flat::CreatePsyonixBotPlayer(*builder, structPlayerConfig.BotSkill).Union();
			}
		}
		else
		{
			if (structPlayerConfig.RLBotControlled)
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
		configBuilder.add_team(structPlayerConfig.Team);
		configBuilder.add_variety(player);
		configBuilder.add_variety_type(variety);

		return configBuilder.Finish();
	}

	flatbuffers::Offset<rlbot::flat::MutatorSettings> buildMutatorSettings(flatbuffers::FlatBufferBuilder* builder, MutatorSettings structMutators)
	{
		rlbot::flat::MutatorSettingsBuilder mutatorBuilder(*builder);
		// We rely on the enums in the flatbuffer being in the exact same order as the ones in the struct, and therefore being numbered the same.
		mutatorBuilder.add_matchLength(static_cast<rlbot::flat::MatchLength>(structMutators.MatchLength));
		mutatorBuilder.add_maxScore(static_cast<rlbot::flat::MaxScore>(structMutators.MaxScore));
		mutatorBuilder.add_overtimeOption(static_cast<rlbot::flat::OvertimeOption>(structMutators.OvertimeOptions));
		mutatorBuilder.add_seriesLengthOption(static_cast<rlbot::flat::SeriesLengthOption>(structMutators.SeriesLengthOptions));
		mutatorBuilder.add_gameSpeedOption(static_cast<rlbot::flat::GameSpeedOption>(structMutators.GameSpeedOptions));
		mutatorBuilder.add_ballMaxSpeedOption(static_cast<rlbot::flat::BallMaxSpeedOption>(structMutators.BallMaxSpeedOptions));
		mutatorBuilder.add_ballTypeOption(static_cast<rlbot::flat::BallTypeOption>(structMutators.BallTypeOptions));
		mutatorBuilder.add_ballWeightOption(static_cast<rlbot::flat::BallWeightOption>(structMutators.BallWeightOptions));
		mutatorBuilder.add_ballSizeOption(static_cast<rlbot::flat::BallSizeOption>(structMutators.BallSizeOptions));
		mutatorBuilder.add_ballBouncinessOption(static_cast<rlbot::flat::BallBouncinessOption>(structMutators.BallBouncinessOptions));
		mutatorBuilder.add_boostOption(static_cast<rlbot::flat::BoostOption>(structMutators.BoostOptions));
		mutatorBuilder.add_rumbleOption(static_cast<rlbot::flat::RumbleOption>(structMutators.RumbleOptions));
		mutatorBuilder.add_boostStrengthOption(static_cast<rlbot::flat::BoostStrengthOption>(structMutators.BoostStrengthOptions));
		mutatorBuilder.add_gravityOption(static_cast<rlbot::flat::GravityOption>(structMutators.GravityOptions));
		mutatorBuilder.add_demolishOption(static_cast<rlbot::flat::DemolishOption>(structMutators.DemolishOptions));
		mutatorBuilder.add_respawnTimeOption(static_cast<rlbot::flat::RespawnTimeOption>(structMutators.RespawnTimeOptions));
		return mutatorBuilder.Finish();
	}


	bool BuildStartMatchMessage(flatbuffers::FlatBufferBuilder* builder, MatchSettings matchSettings)
	{
		std::vector<flatbuffers::Offset<rlbot::flat::PlayerConfiguration>> playerConfigOffsets;

		for (int i = 0; i < matchSettings.NumPlayers; i++)
		{
			playerConfigOffsets.push_back(buildPlayerConfiguration(builder, matchSettings.PlayerConfiguration[i]));
		}

		auto matchSettingsFlat = rlbot::flat::CreateMatchSettings(
			*builder, 
			builder->CreateVector(playerConfigOffsets), 
			static_cast<rlbot::flat::GameMode>(matchSettings.GameMode), 
			static_cast<rlbot::flat::GameMap>(matchSettings.GameMap), 
			matchSettings.SkipReplays, 
			matchSettings.InstantStart, 
			buildMutatorSettings(builder, matchSettings.MutatorSettings),
			static_cast<rlbot::flat::ExistingMatchBehavior>(matchSettings.ExistingMatchBehavior));

		builder->Finish(matchSettingsFlat);

		return true;
	}

	rlbot::flat::Quaternion createQuaternion(Quaternion structQuaternion)
	{
		return rlbot::flat::Quaternion(structQuaternion.X, structQuaternion.Y, structQuaternion.Z, structQuaternion.W);
	}

	flatbuffers::Offset<rlbot::flat::RigidBodyState> createRigidBodyState(flatbuffers::FlatBufferBuilder* builder, RigidBodyState state)
	{
		return rlbot::flat::CreateRigidBodyState(*builder,
			state.Frame,
			&createVector3(state.Location),
			&createQuaternion(state.Rotation),
			&createVector3(state.Velocity),
			&createVector3(state.AngularVelocity));
	}

	flatbuffers::Offset<rlbot::flat::ControllerState> createControllerState(flatbuffers::FlatBufferBuilder* builder, PlayerInput structPlayerInput)
	{
		return rlbot::flat::CreateControllerState(*builder,
			structPlayerInput.Throttle,
			structPlayerInput.Steer,
			structPlayerInput.Pitch,
			structPlayerInput.Yaw,
			structPlayerInput.Roll,
			structPlayerInput.Jump,
			structPlayerInput.Boost,
			structPlayerInput.Handbrake,
			structPlayerInput.UseItem);
	}

	flatbuffers::Offset<rlbot::flat::PlayerRigidBodyState> createPlayerRigid(flatbuffers::FlatBufferBuilder* builder, PlayerRigidBodyState stateStruct)
	{
		auto state = createRigidBodyState(builder, stateStruct.State);
		auto input = createControllerState(builder, stateStruct.Input);

		return rlbot::flat::CreatePlayerRigidBodyState(*builder, state, input);

	}

	flatbuffers::Offset<rlbot::flat::BallRigidBodyState> createBallRigidBody(flatbuffers::FlatBufferBuilder* builder, BallRigidBodyState structBallState)
	{
		return rlbot::flat::CreateBallRigidBodyState(*builder, createRigidBodyState(builder, structBallState.State));
	}

	bool FillRigidBody(flatbuffers::FlatBufferBuilder* builder, RigidBodyTick rigidBodyTick)
	{
		std::vector<flatbuffers::Offset<rlbot::flat::PlayerRigidBodyState>> players;
		flatbuffers::Offset<flatbuffers::Vector<flatbuffers::Offset<rlbot::flat::PlayerRigidBodyState>>> playersOffset;


		for (int i = 0; i < rigidBodyTick.NumPlayers; i++)
		{
			players.push_back(createPlayerRigid(builder, rigidBodyTick.Players[i]));
		}

		playersOffset = builder->CreateVector(players);

		flatbuffers::Offset<rlbot::flat::BallRigidBodyState> ballOffset;

		ballOffset = createBallRigidBody(builder, rigidBodyTick.Ball);

		auto tickOffset = rlbot::flat::CreateRigidBodyTick(*builder, ballOffset, playersOffset);

		builder->Finish(tickOffset);

		return true;
	}
}
