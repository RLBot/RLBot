package rlbot;

import com.sun.javafx.geom.Vec3d;

public class Bot {

    private final Team team;

    public enum Team {
        BLUE,
        ORANGE
    }

    public Bot(Team team) {
        this.team = team;
    }


    public AgentOutput getOutput(AgentInput input) {

        CarData car = input.getMyCarData();

        Vec3d ballPosition = input.ballPosition;
        Vec3d myPosition = car.position;
        CarRotation myRotation = car.rotation;

        float playerDirectionRad = (float) Math.atan2(myRotation.noseVector.z, myRotation.noseVector.x);

        Vec3d toBall = new Vec3d();
        toBall.sub(ballPosition, myPosition);

        float relativeAngleToBallRad = (float) Math.atan2(toBall.z, toBall.x);

        if (Math.abs(playerDirectionRad - relativeAngleToBallRad) > Math.PI) {
            if (playerDirectionRad < 0) {
                playerDirectionRad += Math.PI * 2;
            }
            if (relativeAngleToBallRad < 0) {
                relativeAngleToBallRad += Math.PI * 2;
            }
        }

        return new AgentOutput()
                .withAcceleration(1)
                .withSteer(Math.signum(playerDirectionRad - relativeAngleToBallRad));
    }
}
