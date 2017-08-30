package rlbot;

import com.sun.javafx.geom.Vec3d;

public class CarRotation {

    public Vec3d noseVector;
    public Vec3d roofVector;
    public Vec3d sideVector;

    public CarRotation(Vec3d noseVector, Vec3d roofVector) {

        this.noseVector = noseVector;
        this.roofVector = roofVector;

        this.sideVector = new Vec3d();
        this.sideVector.cross(noseVector, roofVector);
    }
}
