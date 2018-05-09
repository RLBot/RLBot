package rlbot.input;


import rlbot.api.GameData;
import rlbot.vector.Vector3;

public class BallData {
    public final Vector3 position;
    public final Vector3 velocity;
    public final Vector3 spin;

    public BallData(final GameData.BallInfo ballInfo) {
        this.position = Vector3.fromProto(ballInfo.getPhysics().getLocation());
        this.velocity = Vector3.fromProto(ballInfo.getPhysics().getVelocity());
        this.spin = Vector3.fromProto(ballInfo.getPhysics().getAngularVelocity());
    }

    public BallData(final rlbot.flat.BallInfo ball) {
        this.position = Vector3.fromFlatbuffer(ball.physics().location());
        this.velocity = Vector3.fromFlatbuffer(ball.physics().velocity());
        this.spin = Vector3.fromFlatbuffer(ball.physics().angularVelocity());
    }
}
