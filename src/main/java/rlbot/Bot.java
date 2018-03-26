package rlbot;

import rlbot.api.GameData;

public interface Bot {

    int getIndex();

    GameData.ControllerState processInput(GameData.GameTickPacket request);

    void retire();
}
