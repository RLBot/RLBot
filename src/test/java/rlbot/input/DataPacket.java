package rlbot.input;

public class DataPacket {

    public final CarData car;
    public final BallData ball;
    public final int team;
    public final int playerIndex;

    public DataPacket(rlbot.flat.GameTickPacket request, int playerIndex) {

        this.playerIndex = playerIndex;
        this.ball = new BallData(request.ball());

        rlbot.flat.PlayerInfo myPlayerInfo = request.players(playerIndex);
        this.team = myPlayerInfo.team();
        this.car = new CarData(myPlayerInfo, request.gameInfo().secondsElapsed());
    }
}
