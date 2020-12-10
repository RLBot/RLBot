package rlbot.pyinterop;

import rlbot.Bot;
import rlbot.manager.BotManager;

public abstract class SocketServer extends BaseSocketServer {

    private final BotManager botManager;

    public SocketServer(Integer port, BotManager botManager) {
        super(port, botManager);
        this.botManager = botManager;
    }

    protected void ensureBotRegistered(final int index, final String botType, final int team) {
        botManager.ensureBotRegistered(index, team, () -> initBot(index, botType, team));
    }

    protected abstract Bot initBot(final int index, final String botType, final int team);
}
