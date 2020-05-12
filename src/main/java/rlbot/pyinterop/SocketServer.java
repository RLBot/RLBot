package rlbot.pyinterop;

import rlbot.Bot;
import rlbot.manager.BotManager;

public abstract class SocketServer extends BaseSocketServer {

    private final BotManager botManager;

    public SocketServer(Integer port, BotManager botManager) {
        super(port, botManager);
        this.botManager = botManager;
    }

    @Override
    protected void ensureBotRegistered(int index, String botType, int team) {
        botManager.ensureBotRegistered(index, team, () -> initBot(index, botType, team));
    }

    protected abstract Bot initBot(int index, String botType, int team);
}
