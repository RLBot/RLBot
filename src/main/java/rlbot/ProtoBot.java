package rlbot;

import rlbot.api.GameData;

public interface ProtoBot {

    int getIndex();

    ControllerState processInput(GameData.GameTickPacket request);

    void retire();
}
