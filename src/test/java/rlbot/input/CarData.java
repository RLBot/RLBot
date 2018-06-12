package rlbot.input;


import rlbot.vec.Vector3;

public class CarData {
    public final Vector3 position;
    public final Vector3 velocity;
    public final CarOrientation orientation;
    public final double boost;
    public final boolean hasWheelContact;
    public final boolean isSupersonic;
    public final int team;
    public final float elapsedSeconds;

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
