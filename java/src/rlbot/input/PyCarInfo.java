package rlbot.input;

public class PyCarInfo {
    public PyVector3 Location; //  Python type: Vector3
    public PyRotator Rotation; //  Python type: Rotator
    public PyVector3 Velocity; //  Python type: Vector3
    public PyVector3 AngularVelocity; //  Python type: Vector3
    public PyScoreInfo Score; //  Python type: ScoreInfo
    public boolean bDemolished; //  Python type: ctypes.c_bool
    public boolean bSuperSonic; //  Python type: ctypes.c_bool
    public boolean bBot; //  Python type: ctypes.c_bool
    public int PlayerID; //  Python type: ctypes.c_int
    public int Team; //  Python type: ctypes.c_ubyte
    public int Boost; //  Python type: ctypes.c_int
}
