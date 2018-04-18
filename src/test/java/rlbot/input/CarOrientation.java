package rlbot.input;


import rlbot.api.GameData;
import rlbot.vector.Vector3;

public class CarOrientation {

    public Vector3 noseVector;
    public Vector3 roofVector;
    public Vector3 rightVector;

    public CarOrientation(Vector3 noseVector, Vector3 roofVector) {

        this.noseVector = noseVector;
        this.roofVector = roofVector;
        this.rightVector = noseVector.crossProduct(roofVector);
    }

    public static CarOrientation fromPlayerInfo(final GameData.PlayerInfo playerInfo) {
        return convert(
                playerInfo.getRotation().getPitch(),
                playerInfo.getRotation().getYaw(),
                playerInfo.getRotation().getRoll());
    }

    /**
     * All params are in radians.
     */
    private static CarOrientation convert(double pitch, double yaw, double roll) {

        double noseX = -1 * Math.cos(pitch) * Math.cos(yaw);
        double noseY = Math.cos(pitch) * Math.sin(yaw);
        double noseZ = Math.sin(pitch);

        double roofX = Math.cos(roll) * Math.sin(pitch) * Math.cos(yaw) + Math.sin(roll) * Math.sin(yaw);
        double roofY = Math.cos(yaw) * Math.sin(roll) - Math.cos(roll) * Math.sin(pitch) * Math.sin(yaw);
        double roofZ = Math.cos(roll) * Math.cos(pitch);

        return new CarOrientation(new Vector3(noseX, noseY, noseZ), new Vector3(roofX, roofY, roofZ));
    }
}
