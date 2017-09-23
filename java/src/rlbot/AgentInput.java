package rlbot;

import com.sun.javafx.geom.Vec3d;
import rlbot.input.PyCarInfo;
import rlbot.input.PyGameTickPacket;
import rlbot.input.PyRotator;
import rlbot.input.PyVector3;

import java.time.LocalDateTime;

public class AgentInput {

    /**
     * When this is true, we will use the units and conventions from the original API.
     * That means Y will be the height axis, and the field will be approx. 200 units long.
     *
     * When it's false, Z is the height axis, and the field is about 10000 units long.
     */
    public static final boolean LEGACY_MODE = true;

    private static final double RADIANS_PER_ROTATION_UNIT = Math.PI / 32768;
    private static final double LEGACY_UNITS_CONVERSION = 50;

    public final CarData blueCar;
    public final CarData orangeCar;
    public final int blueScore;
    public final int orangeScore;
    public final int blueDemo;
    public final int orangeDemo;
    public final Vec3d ballPosition;
    public final Vec3d ballVelocity;
    public final Bot.Team team;
    public LocalDateTime time;


    /**
     * This is incomplete; it does not extract all the data from gameTickPacket. Extract more if you need it.
     */
    public AgentInput(PyGameTickPacket gameTickPacket, Bot.Team team) {
        this.team = team;
        time = LocalDateTime.now();

        final PyCarInfo blueCarInput;
        final PyCarInfo orangeCarInput;

        if (gameTickPacket.gamecars.get(0).Team == 0) {
            blueCarInput = gameTickPacket.gamecars.get(0);
            orangeCarInput = gameTickPacket.gamecars.get(1);
        } else {
            blueCarInput = gameTickPacket.gamecars.get(1);
            orangeCarInput = gameTickPacket.gamecars.get(0);
        }

        blueScore = blueCarInput.Score.Goals + orangeCarInput.Score.OwnGoals;
        orangeScore = orangeCarInput.Score.Goals + blueCarInput.Score.OwnGoals;
        blueDemo = blueCarInput.Score.Demolitions;
        orangeDemo = orangeCarInput.Score.Demolitions;

        ballPosition = convert(gameTickPacket.gameball.Location);
        ballVelocity = convert(gameTickPacket.gameball.Velocity);

        Vec3d orangePosition = convert(orangeCarInput.Location);
        Vec3d orangeVelocity = convert(orangeCarInput.Velocity);
        CarRotation orangeRotation = convert(orangeCarInput.Rotation);
        double orangeBoost = orangeCarInput.Boost;
        orangeCar = new CarData(orangePosition, orangeVelocity, orangeRotation, orangeBoost,
                orangeCarInput.bSuperSonic, Bot.Team.ORANGE);

        Vec3d bluePosition = convert(blueCarInput.Location);
        Vec3d blueVelocity = convert(blueCarInput.Velocity);
        CarRotation blueRotation = convert(blueCarInput.Rotation);
        double blueBoost = blueCarInput.Boost;
        blueCar = new CarData(bluePosition, blueVelocity, blueRotation, blueBoost,
                blueCarInput.bSuperSonic, Bot.Team.BLUE);
    }


    private CarRotation convert(PyRotator rotation) {

        double noseX = -1 * Math.cos(rotation.Pitch * RADIANS_PER_ROTATION_UNIT) * Math.cos(rotation.Yaw * RADIANS_PER_ROTATION_UNIT);
        double noseY = Math.cos(rotation.Pitch * RADIANS_PER_ROTATION_UNIT) * Math.sin(rotation.Yaw * RADIANS_PER_ROTATION_UNIT);
        double noseZ = Math.sin(rotation.Pitch * RADIANS_PER_ROTATION_UNIT);

        double roofX = Math.cos(rotation.Roll * RADIANS_PER_ROTATION_UNIT) * Math.sin(rotation.Pitch * RADIANS_PER_ROTATION_UNIT) * Math.cos(rotation.Yaw * RADIANS_PER_ROTATION_UNIT) + Math.sin(rotation.Roll * RADIANS_PER_ROTATION_UNIT) * Math.sin(rotation.Yaw * RADIANS_PER_ROTATION_UNIT);
        double roofY = Math.cos(rotation.Yaw * RADIANS_PER_ROTATION_UNIT) * Math.sin(rotation.Roll * RADIANS_PER_ROTATION_UNIT) - Math.cos(rotation.Roll * RADIANS_PER_ROTATION_UNIT) * Math.sin(rotation.Pitch * RADIANS_PER_ROTATION_UNIT) * Math.sin(rotation.Yaw * RADIANS_PER_ROTATION_UNIT);
        double roofZ = Math.cos(rotation.Roll * RADIANS_PER_ROTATION_UNIT) * Math.cos(rotation.Pitch * RADIANS_PER_ROTATION_UNIT);

        if (LEGACY_MODE) {
            return new CarRotation(new Vec3d(noseX, noseZ, noseY), new Vec3d(roofX, roofZ, roofY));
        } else {
            return new CarRotation(new Vec3d(noseX, noseY, noseZ), new Vec3d(roofX, roofY, roofZ));
        }

    }

    private Vec3d convert(PyVector3 location) {

        if (LEGACY_MODE) {
            // Invert the X value so that the axes make more sense.
            return new Vec3d(-location.X / LEGACY_UNITS_CONVERSION, location.Z / LEGACY_UNITS_CONVERSION, location.Y / LEGACY_UNITS_CONVERSION);
        } else {
            // Invert the X value so that the axes make more sense.
            return new Vec3d(-location.X, location.Y, location.Z);
        }
    }

    public CarData getMyCarData() {
        return team == Bot.Team.BLUE ? blueCar : orangeCar;
    }

    public CarData getEnemyCarData() {
        return team == Bot.Team.BLUE ? orangeCar : blueCar;
    }
}
