package rlbot;

import com.sun.javafx.geom.Vec3d;

public class CarData {
    public final Vec3d position;
    public final Vec3d velocity;
    public final CarRotation rotation;
    public final double boost;
    public boolean isSupersonic;
    public final Bot.Team team;

    public CarData(Vec3d position, Vec3d velocity, CarRotation rotation, double boost,
                   boolean isSupersonic, Bot.Team team) {
        this.position = position;
        this.velocity = velocity;
        this.rotation = rotation;
        this.boost = boost;
        this.isSupersonic = isSupersonic;
        this.team = team;
    }
}
