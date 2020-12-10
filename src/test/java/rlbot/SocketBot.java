package rlbot;

import rlbot.flat.GameTickPacket;
import rlbot.input.CarData;
import rlbot.input.DataPacket;
import rlbot.output.ControlsOutput;
import rlbot.vec.Vector2;

public class SocketBot extends BaseBot {

    public SocketBot(int playerIndex, int team) {
        super(playerIndex, team);

        System.out.println("Constructed socket bot " + playerIndex);
    }

    private ControlsOutput processInput(DataPacket input) {

        Vector2 ballPosition = input.ball.position.flatten();
        CarData myCar = input.car;
        Vector2 carPosition = myCar.position.flatten();
        Vector2 carDirection = myCar.orientation.noseVector.flatten();
        Vector2 carToBall = ballPosition.minus(carPosition);

        double steerCorrectionRadians = carDirection.correctionAngle(carToBall);
        float steer;
        if (steerCorrectionRadians > 0) {
            steer = -1;
        } else {
            steer = 1;
        }

        return new ControlsOutput()
                .withSteer(steer)
                .withThrottle(1)
                .withUseItem(myCar.velocity.y > 0);
    }

    @Override
    public ControllerState processInput(GameTickPacket gameTickPacket) {
        if (gameTickPacket.playersLength() <= index || gameTickPacket.ball() == null) {
            return new ControlsOutput();
        }
        DataPacket dataPacket = new DataPacket(gameTickPacket, index);
        return processInput(dataPacket);
    }

    public void retire() {
        System.out.println("Retiring sample bot " + index);
    }
}
