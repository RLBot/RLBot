package rlbot;

import rlbot.cppinterop.RLBotDll;
import rlbot.cppinterop.RLBotInterfaceException;
import rlbot.flat.*;
import rlbot.gamestate.CarState;
import rlbot.gamestate.DesiredRotation;
import rlbot.gamestate.GameState;
import rlbot.gamestate.PhysicsState;
import rlbot.input.CarData;
import rlbot.input.DataPacket;
import rlbot.input.DropshotTile;
import rlbot.input.FieldInfoManager;
import rlbot.manager.BotLoopRenderer;
import rlbot.output.ControlsOutput;
import rlbot.render.Renderer;
import rlbot.vec.Vector2;

import java.awt.Color;
import java.io.IOException;

public class SampleBot extends BaseBot {

    private FieldInfoManager fieldInfoManager = new FieldInfoManager();

    public SampleBot(int playerIndex, int team) {
        super(playerIndex, team);

        System.out.println("Constructed sample bot " + playerIndex);
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
                    .withCarState(this.index, new CarState()
                            .withPhysics(new PhysicsState()
                                    .withRotation(new DesiredRotation((float) Math.PI,0F, 0F))));

            RLBotDll.setGameState(gameState.buildPacket());
            RLBotDll.sendQuickChat(this.index, false, QuickChatSelection.Apologies_Oops);
            try {
                MatchSettings matchSettings = RLBotDll.getMatchSettings();
                System.out.println("Game mode: " + GameMode.name(matchSettings.gameMode()));
                System.out.println("Game map: " + GameMap.name(matchSettings.gameMap()));
                System.out.println("Rumble option: " + RumbleOption.name(matchSettings.mutatorSettings().rumbleOption()));
            } catch (RLBotInterfaceException e) {
                e.printStackTrace();
            }
        }

        try {
            QuickChatMessages quickChatMessages = receiveQuickChat();
            if (quickChatMessages.messagesLength() > 0) {
                RLBotDll.sendQuickChat(this.index, false, QuickChatSelection.Reactions_Wow);
            }
        } catch (RLBotInterfaceException e) {
            e.printStackTrace();
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
                .withThrottle(1)
                .withUseItem(myCar.velocity.y > 0);
    }

    @Override
    public ControllerState processInput(rlbot.flat.GameTickPacket gameTickPacket) {
        if (gameTickPacket.playersLength() <= index || gameTickPacket.ball() == null) {
            return new ControlsOutput();
        }
        DataPacket dataPacket = new DataPacket(gameTickPacket, index);
        fieldInfoManager.addPacketInfo(gameTickPacket);
        return processInput(dataPacket);
    }

    public void retire() {
        System.out.println("Retiring sample bot " + index);
    }
}
