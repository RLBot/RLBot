package rlbot.input;

import rlbot.vector.Vector3;

import java.util.ArrayList;
import java.util.List;

public class DataPacket {

    public final CarData car;
    public final BallData ball;
    public final int team;
    public final int playerIndex;
    public final List<FullBoost> fullBoosts = new ArrayList<>(6);
    public final rlbot.api.GameData.GameInfo matchInfo;

    public DataPacket(rlbot.api.GameData.GameTickPacket request, int playerIndex) {

        this.playerIndex = playerIndex;
        this.matchInfo = request.getGameInfo();
        this.ball = new BallData(request.getBall());

        rlbot.api.GameData.PlayerInfo myPlayerInfo = request.getPlayers(playerIndex);
        this.team = myPlayerInfo.getTeam();
        this.car = new CarData(myPlayerInfo, request.getGameInfo().getSecondsElapsed());

        for (rlbot.api.GameData.BoostInfo boostInfo: request.getBoostPadsList()) {
            Vector3 location = Vector3.fromProto(boostInfo.getLocation());
            if (FullBoost.isFullBoostLocation(location)) {
                fullBoosts.add(new FullBoost(location, boostInfo.getIsActive()));
            }
        }
    }
}
