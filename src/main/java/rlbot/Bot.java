package rlbot;

import rlbot.flat.GameTickPacket;

public interface Bot {

    int getIndex();

    ControllerState processInput(GameTickPacket request);

    void retire();
}
