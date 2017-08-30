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

        Vec3d ballPosition = input.ballPosition;
        Vec3d myPosition = team == Team.BLUE ? input.bluePosition : input.orangePosition;
        CarRotation myRotation = team == Team.BLUE ? input.blueRotation : input.orangeRotation;

        float playerDirectionRad = (float) Math.atan2(myRotation.noseVector.x, myRotation.noseVector.z);

        float relativeAngleToBallRad = (float) Math.atan2(ballPosition.x - myPosition.x, ballPosition.z - myPosition.z);

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
