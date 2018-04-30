package rlbot.input;

public class DataPacket {

    public final CarData car;
    public final BallData ball;
    public final int team;
    public final int playerIndex;
    public final rlbot.api.GameData.GameInfo matchInfo;

    public DataPacket(rlbot.api.GameData.GameTickPacket request, int playerIndex) {

        this.playerIndex = playerIndex;
        this.matchInfo = request.getGameInfo();
        this.ball = new BallData(request.getBall());

        rlbot.api.GameData.PlayerInfo myPlayerInfo = request.getPlayers(playerIndex);
        this.team = myPlayerInfo.getTeam();
        this.car = new CarData(myPlayerInfo, request.getGameInfo().getSecondsElapsed());
    }
}
