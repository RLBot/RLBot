package rlbot;

import io.grpc.stub.StreamObserver;
import rlbot.api.BotGrpc;
import rlbot.api.GameData;
import rlbot.input.DataPacket;

import java.util.HashMap;
import java.util.Map;

public class GrpcService extends BotGrpc.BotImplBase {

    private Map<Integer, Bot> bots = new HashMap<>();

    GrpcService() {
    }

    @Override
    public void getControllerState(GameData.GameTickPacket request, StreamObserver<GameData.ControllerState> responseObserver) {
        responseObserver.onNext(doGetControllerState(request));
        responseObserver.onCompleted();
    }

    private GameData.ControllerState doGetControllerState(GameData.GameTickPacket request) {

        try {
            int playerIndex = request.getPlayerIndex();

            // Do nothing if we know nothing about our car
            if (request.getPlayersCount() <= playerIndex) {
                return new ControlsOutput().toControllerState();
            }

            DataPacket translatedInput = new DataPacket(request, playerIndex);
            Bot bot = bots.computeIfAbsent(playerIndex, idx -> new Bot());

            return bot.processInput(translatedInput).toControllerState();
        } catch (Exception e) {
            e.printStackTrace();
            return new ControlsOutput().toControllerState();
        }

    }
}
