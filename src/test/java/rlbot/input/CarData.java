package rlbot.input;


import rlbot.api.GameData;
import rlbot.vector.Vector3;

public class CarData {
    public final Vector3 position;
    public final Vector3 velocity;
    public final CarOrientation orientation;
    public final double boost;
    public final boolean hasWheelContact;
    public final boolean isSupersonic;
    public final int team;
    public final float elapsedSeconds;

    public CarData(GameData.PlayerInfo playerInfo, float elapsedSeconds) {

        this.position = Vector3.fromProto(playerInfo.getPhysics().getLocation());
        this.velocity = Vector3.fromProto(playerInfo.getPhysics().getVelocity());
        this.orientation = CarOrientation.fromPlayerInfo(playerInfo);
        this.boost = playerInfo.getBoost();
        this.isSupersonic = playerInfo.getIsSupersonic();
        this.team = playerInfo.getTeam();
        this.hasWheelContact = playerInfo.getHasWheelContact();
        this.elapsedSeconds = elapsedSeconds;
    }

    public CarData(rlbot.flat.PlayerInfo playerInfo, float elapsedSeconds) {
        this.position = Vector3.fromFlatbuffer(playerInfo.physics().location());
        this.velocity = Vector3.fromFlatbuffer(playerInfo.physics().velocity());
        this.orientation = CarOrientation.fromFlatbuffer(playerInfo);
        this.boost = playerInfo.boost();
        this.isSupersonic = playerInfo.isSupersonic();
        this.team = playerInfo.team();
        this.hasWheelContact = playerInfo.hasWheelContact();
        this.elapsedSeconds = elapsedSeconds;
    }
}
