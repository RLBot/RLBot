package rlbot.gamestate;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.flat.DesiredGameInfoState;

/**
 * See https://github.com/RLBot/RLBotJavaExample/wiki/Manipulating-Game-State
 */
public class GameInfoState {
    private Float worldGravityZ;
    private Float gameSpeed;

    public GameInfoState() {
    }

    public Float getWorldGravityZ() {
        return worldGravityZ;
    }

    /**
     * Standard gravity is -650
     *
     * Warning: Setting 0 will not work due to a quirk of Rocket League.
     * To get a zero-gravity situation, pass a very small number like 0.0000001
     */
    public GameInfoState withWorldGravityZ(Float worldGravityZ) {
        this.worldGravityZ = worldGravityZ;
        return this;
    }

    public Float getGameSpeed() {
        return gameSpeed;
    }

    public GameInfoState withGameSpeed(Float gameSpeed) {
        this.gameSpeed = gameSpeed;
        return this;
    }

    public int toFlatbuffer(FlatBufferBuilder builder) {
        DesiredGameInfoState.startDesiredGameInfoState(builder);
        if (worldGravityZ != null) {
            DesiredGameInfoState.addWorldGravityZ(builder, rlbot.flat.Float.createFloat(builder, worldGravityZ));
        }
        if (gameSpeed != null) {
            DesiredGameInfoState.addGameSpeed(builder, rlbot.flat.Float.createFloat(builder, gameSpeed));
        }
        return DesiredGameInfoState.endDesiredGameInfoState(builder);
    }
}
