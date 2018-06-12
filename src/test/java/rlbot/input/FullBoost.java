package rlbot.input;


import rlbot.vec.Vector3;

import java.util.Arrays;
import java.util.List;

public class FullBoost {

    private static final int MIDFIELD_BOOST_WIDTH = 3584;
    private static final int CORNER_BOOST_WIDTH = 3072;
    private static final int CORNER_BOOST_DEPTH = 4096;

    private static final List<Vector3> fullBoostLocations = Arrays.asList(
            new Vector3(MIDFIELD_BOOST_WIDTH, 0, 0),
            new Vector3(-MIDFIELD_BOOST_WIDTH, 0, 0),
            new Vector3(-CORNER_BOOST_WIDTH, -CORNER_BOOST_DEPTH, 0),
            new Vector3(-CORNER_BOOST_WIDTH, CORNER_BOOST_DEPTH, 0),
            new Vector3(CORNER_BOOST_WIDTH, -CORNER_BOOST_DEPTH, 0),
            new Vector3(CORNER_BOOST_WIDTH, CORNER_BOOST_DEPTH, 0)
    );

    public Vector3 location;
    public boolean isActive;

    public FullBoost(Vector3 location, boolean isActive) {
        this.location = location;
        this.isActive = isActive;
    }

    public static boolean isFullBoostLocation(Vector3 location) {
        for (Vector3 boostLoc: fullBoostLocations) {
            if (boostLoc.distance(location) < 10) {
                return true;
            }
        }
        return false;
    }

}
