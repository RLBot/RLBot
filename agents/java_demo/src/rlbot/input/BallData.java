package rlbot.input;


import rlbot.api.GameData;
import rlbot.vector.Vector3;

public class BallData {
    public final Vector3 position;
    public final Vector3 velocity;
    public final Vector3 spin;

    public BallData(final GameData.BallInfo ballInfo) {
        this.position = Vector3.fromProto(ballInfo.getLocation());
        this.velocity = Vector3.fromProto(ballInfo.getLocation());
        this.spin = Vector3.fromProto(ballInfo.getAngularVelocity());
    }
}
