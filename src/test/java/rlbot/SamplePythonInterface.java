package rlbot;

import rlbot.manager.BotManager;
import rlbot.pyinterop.SocketServer;

public class SamplePythonInterface extends SocketServer {

    public SamplePythonInterface(int port, BotManager botManager) {
        super(port, botManager);
    }

    protected Bot initBot(int index, String botType, int team) {
        return new SocketBot(index, team);
    }
}
