package rlbot.input;


import rlbot.api.GameData;
import rlbot.vector.Vector3;

public class CarData {
    public final Vector3 position;
    public final Vector3 velocity;
    public final CarOrientation orientation;
    public final double boost;
    public final boolean isMidair;
    public final boolean isSupersonic;
    public final int team;
    public final float elapsedSeconds;

    public CarData(GameData.PlayerInfo playerInfo, float elapsedSeconds) {

        this.position = Vector3.fromProto(playerInfo.getLocation());
        this.velocity = Vector3.fromProto(playerInfo.getVelocity());
        this.orientation = CarOrientation.fromPlayerInfo(playerInfo);
        this.boost = playerInfo.getBoost();
        this.isSupersonic = playerInfo.getIsSupersonic();
        this.team = playerInfo.getTeam();
        this.isMidair = playerInfo.getIsMidair();
        this.elapsedSeconds = elapsedSeconds;
    }
}
