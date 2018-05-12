package rlbot.input;


import rlbot.vector.Vector2;
import rlbot.vector.Vector3;

import java.util.Arrays;
import java.util.List;

public class FullBoost {

    private static final int MIDFIELD_BOOST_WIDTH = 3584;
    private static final int CORNER_BOOST_WIDTH = 3072;
    private static final int CORNER_BOOST_DEPTH = 4096;

    private static final List<Vector2> fullBoostLocations = Arrays.asList(
            new Vector2(MIDFIELD_BOOST_WIDTH, 0),
            new Vector2(-MIDFIELD_BOOST_WIDTH, 0),
            new Vector2(-CORNER_BOOST_WIDTH, -CORNER_BOOST_DEPTH),
            new Vector2(-CORNER_BOOST_WIDTH, CORNER_BOOST_DEPTH),
            new Vector2(CORNER_BOOST_WIDTH, -CORNER_BOOST_DEPTH),
            new Vector2(CORNER_BOOST_WIDTH, CORNER_BOOST_DEPTH)
    );

    public Vector3 location;
    public boolean isActive;

    public FullBoost(Vector3 location, boolean isActive) {
        this.location = location;
        this.isActive = isActive;
    }

    public static boolean isFullBoostLocation(Vector3 location) {
        for (Vector2 boostLoc: fullBoostLocations) {
            if (boostLoc.distance(location.flatten()) < 10) {
                return true;
            }
        }
        return false;
    }

}
