package rlbot;

import rlbot.flat.GameTickPacket;

public interface FlatBot {

    int getIndex();

    ControllerState processInput(GameTickPacket request);

    void retire();
}
