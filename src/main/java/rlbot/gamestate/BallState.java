package rlbot.gamestate;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.flat.DesiredBallState;
import rlbot.flat.DesiredPhysics;

public class BallState {
    private PhysicsState physics;

    public BallState() {
    }

    public BallState(PhysicsState physics) {
        this.physics = physics;
    }

    public PhysicsState getPhysics() {
        return physics;
    }

    public BallState withPhysics(PhysicsState physics) {
        this.physics = physics;
        return this;
    }

    public int toFlatbuffer(FlatBufferBuilder builder) {

        Integer physicsOffset = physics == null ? null : physics.toFlatbuffer(builder);

        DesiredBallState.startDesiredBallState(builder);
        if (physicsOffset != null) {
            DesiredBallState.addPhysics(builder, physicsOffset);
        }
        return DesiredPhysics.endDesiredPhysics(builder);
    }
}
