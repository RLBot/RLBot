package rlbot.pyinterop;

import rlbot.Bot;
import rlbot.manager.HivemindManager;

public abstract class HiveSocketServer extends SocketServer {

    private final HivemindManager hivemindManager;

    public HiveSocketServer(Integer port, HivemindManager hivemindManager) {
        super(port, hivemindManager);
        this.hivemindManager = hivemindManager;
    }

    @Override
    protected void ensureBotRegistered(int index, String botType, int team) {
        hivemindManager.ensureBotRegistered(index, team);
    }

    @Override
    protected Bot initBot(int index, String botType, int team) {
        return null;
    }
}
