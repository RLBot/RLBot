package rlbot;

import rlbot.cppinterop.RLBotDll;
import rlbot.flat.BallPrediction;
import rlbot.flat.Vector3;
import rlbot.gamestate.*;
import rlbot.input.CarData;
import rlbot.input.DataPacket;
import rlbot.input.DropshotTile;
import rlbot.input.FieldInfoManager;
import rlbot.manager.BotLoopRenderer;
import rlbot.output.ControlsOutput;
import rlbot.render.NamedRenderer;
import rlbot.render.Renderer;
import rlbot.vec.DesiredVec;
import rlbot.vec.Vector2;

import java.awt.*;
import java.io.IOException;

public class SampleBot implements Bot {

    private final int playerIndex;
    private final NamedRenderer triangleRenderer;
    private FieldInfoManager fieldInfoManager = new FieldInfoManager();

    public SampleBot(int playerIndex) {
        this.playerIndex = playerIndex;
        System.out.println("Constructed sample bot " + playerIndex);

        triangleRenderer = new NamedRenderer("Triangle" + playerIndex);
        triangleRenderer.startPacket();
        triangleRenderer.drawLine2d(Color.cyan, new Point(50, 50), new Point(20, 80));
        triangleRenderer.drawLine2d(Color.cyan, new Point(20, 80), new Point(80, 80));
        triangleRenderer.drawLine2d(Color.cyan, new Point(50, 50), new Point(80, 80));
        triangleRenderer.finishAndSend();
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

        Renderer renderer = BotLoopRenderer.forBotLoop(this);
        renderer.drawLine3d(Color.BLUE, myCar.position, input.ball.position);
        renderer.drawString3d("It's me", Color.green, myCar.position, 2, 2);
        renderer.drawCenteredRectangle3d(Color.black, input.ball.position, 20, 20, false);

        for (DropshotTile tile: fieldInfoManager.getDropshotTiles()) {
            if (tile.state == DropshotTile.State.OPEN) {
                renderer.drawCenteredRectangle3d(Color.BLACK, tile.location, 10, 10, true);
            }
        }

        if (myCar.position.z > 100) {
            GameState gameState = new GameState()
                    .withCarState(this.playerIndex, new CarState()
                            .withPhysics(new PhysicsState()
                                    .withRotation(new DesiredRotation((float) Math.PI,0F, 0F))));

            RLBotDll.setGameState(gameState.buildPacket());
        } else {

            Float xVel = input.ball.velocity.x + 20;
            GameState gameState = new GameState()
                    .withBallState(new BallState().withPhysics(new PhysicsState().withVelocity(new DesiredVec().withX(xVel))));

            RLBotDll.setGameState(gameState.buildPacket());
        }

        if (input.ball.position.z > 1000) {
            triangleRenderer.eraseFromScreen();
        }

        try {
            final BallPrediction ballPrediction = RLBotDll.getBallPrediction();

            Vector3 location = ballPrediction.slices(ballPrediction.slicesLength() / 2).physics().location();
            renderer.drawLine3d(Color.CYAN, input.ball.position, rlbot.vec.Vector3.fromFlatbuffer(location));

        } catch (IOException e) {
            // Ignore
        }

        return new ControlsOutput()
                .withSteer(steer)
                .withThrottle(1);
    }


    @Override
    public int getIndex() {
        return this.playerIndex;
    }

    @Override
    public ControllerState processInput(rlbot.flat.GameTickPacket gameTickPacket) {
        if (gameTickPacket.playersLength() <= playerIndex || gameTickPacket.ball() == null) {
            return new ControlsOutput();
        }
        DataPacket dataPacket = new DataPacket(gameTickPacket, playerIndex);
        fieldInfoManager.addPacketInfo(gameTickPacket);
        return processInput(dataPacket);
    }

    public void retire() {
        System.out.println("Retiring sample bot " + playerIndex);
    }
}
