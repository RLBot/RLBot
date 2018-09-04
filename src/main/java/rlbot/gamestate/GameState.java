package rlbot.gamestate;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.flat.DesiredGameState;
import rlbot.flat.GameTickPacket;
import rlbot.render.RenderPacket;

import java.util.*;

/**
 * See https://github.com/RLBot/RLBotJavaExample/wiki/Manipulating-Game-State
 */
public class GameState {

    private Map<Integer, CarState> carStates = new HashMap<>();
    private BallState ballState;


    public GameState() {
    }

    public BallState getBallState() {
        return ballState;
    }

    public GameState withBallState(BallState ballState) {
        this.ballState = ballState;
        return this;
    }

    public CarState getCarState(final int playerIndex) {
        return carStates.get(playerIndex);
    }

    public GameState withCarState(final int playerIndex,final CarState carState) {
        carStates.put(playerIndex, carState);
        return this;
    }

    public GameStatePacket buildPacket() {

        FlatBufferBuilder builder = new FlatBufferBuilder(100);
        Integer ballStateOffset = ballState == null ? null : ballState.toFlatbuffer(builder);

        int numElements = carStates.keySet().stream().mapToInt(i -> i + 1).max().orElse(0);

        List<Integer> carOffsets = new ArrayList<>(numElements);

        for (int i = 0; i < numElements; i++) {
            if (carStates.containsKey(i)) {
                carOffsets.add(carStates.get(i).toFlatbuffer(builder));
            } else {
                carOffsets.add(new CarState().toFlatbuffer(builder));
            }
        }

        int[] carIntOffsets = carOffsets.stream().mapToInt(i -> i).toArray();
        int carStatesOffset = DesiredGameState.createCarStatesVector(builder, carIntOffsets);

        DesiredGameState.startDesiredGameState(builder);
        if (ballStateOffset != null) {
            DesiredGameState.addBallState(builder, ballStateOffset);
        }
        DesiredGameState.addCarStates(builder, carStatesOffset);

        int desiredStateOffset = DesiredGameState.endDesiredGameState(builder);

        builder.finish(desiredStateOffset);
        byte[] bytes = builder.sizedByteArray();

        return new GameStatePacket(bytes);
    }
}
