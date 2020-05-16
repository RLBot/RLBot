package rlbot.pyinterop;

import rlbot.manager.HivemindManager;

public class HiveSocketServer extends BaseSocketServer {

    private final HivemindManager hivemindManager;

    public HiveSocketServer(Integer port, HivemindManager hivemindManager) {
        super(port, hivemindManager);
        this.hivemindManager = hivemindManager;
    }

    @Override
    protected void ensureBotRegistered(int index, String botType, int team) {
        hivemindManager.ensureBotRegistered(index, team, botType);
    }
}
