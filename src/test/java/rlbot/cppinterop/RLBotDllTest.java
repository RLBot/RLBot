package rlbot.cppinterop;

import com.google.flatbuffers.FlatBufferBuilder;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import rlbot.flat.*;
import rlbot.gamestate.CarState;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class RLBotDllTest {

    @BeforeAll
    static void initialize() throws IOException {
        RLBotDll.initialize("src/main/python/rlbot/dll/RLBot_Core_Interface.dll");
    }

    /**
     * To run this test successfully, you must open rocket league and inject the core dll
     * before starting.
     */
    @Disabled
    @Test
    void startMatch() {
        FlatBufferBuilder matchSettingsBuilder = new FlatBufferBuilder();

        int paintOffset = LoadoutPaint.createLoadoutPaint(matchSettingsBuilder,
                1, 1, 1, 1, 1, 1, 1, 1);

        int loadoutOffset = PlayerLoadout.createPlayerLoadout(matchSettingsBuilder, 2, 2,
                2, 2, 2, 2, 2, 2, 2, 2, 2,
                2, 2, paintOffset);

        RLBotPlayer.startRLBotPlayer(matchSettingsBuilder);
        int playerClassOffset = RLBotPlayer.endRLBotPlayer(matchSettingsBuilder);

        int nameOffset = matchSettingsBuilder.createString("JavaUnitTest");

        int playerConfigurationOffset = PlayerConfiguration.createPlayerConfiguration(matchSettingsBuilder, PlayerClass.RLBotPlayer, playerClassOffset,
                nameOffset, 0, loadoutOffset);

        int playerConfigurationsOffset = MatchSettings.createPlayerConfigurationsVector(matchSettingsBuilder, new int[]{playerConfigurationOffset});

        int mutatorsOffset = MutatorSettings.createMutatorSettings(matchSettingsBuilder, MatchLength.Ten_Minutes,
                MaxScore.Five_Goals, OvertimeOption.Five_Max_Random_Team, SeriesLengthOption.Three_Games, GameSpeedOption.Default,
                BallMaxSpeedOption.Fast, BallTypeOption.Cube, BallWeightOption.Light, BallSizeOption.Small, BallBouncinessOption.Default,
                BoostOption.Unlimited_Boost, RumbleOption.No_Rumble, BoostStrengthOption.OneAndAHalf, GravityOption.Low, DemolishOption.Default,
                RespawnTimeOption.Three_Seconds);


        MatchSettings.startMatchSettings(matchSettingsBuilder);
        MatchSettings.addPlayerConfigurations(matchSettingsBuilder, playerConfigurationsOffset);
        MatchSettings.addGameMode(matchSettingsBuilder, GameMode.Hoops);
        MatchSettings.addGameMap(matchSettingsBuilder, GameMap.Hoops_DunkHouse);
        MatchSettings.addSkipReplays(matchSettingsBuilder, false);
        MatchSettings.addInstantStart(matchSettingsBuilder, false);
        MatchSettings.addMutatorSettings(matchSettingsBuilder, mutatorsOffset);
        MatchSettings.addExistingMatchBehavior(matchSettingsBuilder, ExistingMatchBehavior.Restart_If_Different);
        int matchSettingsOffset = MatchSettings.endMatchSettings(matchSettingsBuilder);

        matchSettingsBuilder.finish(matchSettingsOffset);

        RLBotDll.startMatch(matchSettingsBuilder);
    }
}
