package rlbot.input;

import java.util.List;

public class PyGameTickPacket {
    public List<PyCarInfo> gamecars; // Python type: gamecars * maxCars
    public int numCars; // Python type: ctypes.c_int
    public List<PyBoostInfo> gameBoosts; // Python type: BoostInfo * maxBoosts
    public int numBoosts; // Python type: ctypes.c_int
    public PyBallInfo gameball; // Python type: BallInfo
    public PyGameInfo gameInfo;
}
