package rlbot.input;

import rlbot.flat.TileState;
import rlbot.vec.Vector3;

public class DropshotTile {

    public final Vector3 location;
    public State state;

    public DropshotTile(final rlbot.flat.GoalInfo goalInfo) {
        location = Vector3.fromFlatbuffer(goalInfo.location());
    }

    public void setState(final rlbot.flat.DropshotTile tile) {
        state = convertState(tile.tileState());
    }

    private State convertState(byte tileState) {
        switch (tileState) {
            case (TileState.Unknown):
                return State.UNKNOWN;
            case (TileState.Filled):
                return State.FILLED;
            case (TileState.Damaged):
                return State.DAMAGED;
            case (TileState.Open):
                return State.OPEN;
            default:
                return State.UNKNOWN;
        }
    }

    public enum State {
        UNKNOWN,
        FILLED,
        DAMAGED,
        OPEN
    }
}
