package rlbot.input;


import rlbot.vec.Vector3;

public class BallData {
    public final Vector3 position;
    public final Vector3 velocity;
    public final Vector3 spin;

    public BallData(final rlbot.flat.BallInfo ball) {
        this.position = Vector3.fromFlatbuffer(ball.physics().location());
        this.velocity = Vector3.fromFlatbuffer(ball.physics().velocity());
        this.spin = Vector3.fromFlatbuffer(ball.physics().angularVelocity());
    }
}
