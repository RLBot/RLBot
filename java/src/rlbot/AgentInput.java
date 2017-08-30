package rlbot;

import com.sun.javafx.geom.Vec3d;

import java.util.ArrayList;

public class AgentInput {
    public final int blueScore;
    public final int orangeScore;
    public final int blueDemo;
    public final int orangeDemo;
    public final Vec3d ballPosition;
    public final Vec3d ballVelocity;
    public final Vec3d orangePosition;
    public final Vec3d bluePosition;
    public final CarRotation blueRotation;
    public final CarRotation orangeRotation;
    public final double orangeBoost;
    public final double blueBoost;
    public final Vec3d orangeVelocity;
    public final Vec3d blueVelocity;


    /**
     * This is based on PlayHelper.py. It is incomplete, add more data as you need it.
     */
    public AgentInput(ArrayList<ArrayList<Double>> input) {

        ArrayList<Double> neuralInputs = input.get(0);
        ArrayList<Double> scoring = input.get(1);

        blueScore = scoring.get(0).intValue();
        orangeScore = scoring.get(1).intValue();
        blueDemo = scoring.get(2).intValue();
        orangeDemo = scoring.get(3).intValue();

        ballPosition = new Vec3d(neuralInputs.get(7), neuralInputs.get(6), neuralInputs.get(2));
        ballVelocity = new Vec3d(neuralInputs.get(31), neuralInputs.get(32), neuralInputs.get(33));

        orangePosition = new Vec3d(neuralInputs.get(18), neuralInputs.get(17), neuralInputs.get(3));
        orangeVelocity = new Vec3d(neuralInputs.get(34), neuralInputs.get(35), neuralInputs.get(36));
        orangeRotation = new CarRotation(new Vec3d(neuralInputs.get(19), neuralInputs.get(25), neuralInputs.get(22)),
                new Vec3d(neuralInputs.get(21), neuralInputs.get(24), neuralInputs.get(27)));
        orangeBoost = neuralInputs.get(37);

        bluePosition = new Vec3d(neuralInputs.get(5), neuralInputs.get(4), neuralInputs.get(1));
        blueVelocity = new Vec3d(neuralInputs.get(28), neuralInputs.get(29), neuralInputs.get(30));
        blueRotation = new CarRotation(new Vec3d(neuralInputs.get(8), neuralInputs.get(14), neuralInputs.get(11)),
                new Vec3d(neuralInputs.get(10), neuralInputs.get(16),  neuralInputs.get(13)));
        blueBoost = neuralInputs.get(0);
    }
}
