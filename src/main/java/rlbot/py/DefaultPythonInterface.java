package rlbot.py;

import rlbot.Bot;
import rlbot.manager.BotManager;

/**
 * The public methods of this class will be called directly from the python component of the RLBot framework.
 */
public abstract class DefaultPythonInterface implements PythonInterface {

    private final BotManager botManager;

    public DefaultPythonInterface(BotManager botManager) {
        this.botManager = botManager;
    }

    public void ensureStarted() {
        botManager.ensureStarted();
    }

    public void shutdown() {
        botManager.shutDown();
    }

    public void ensureBotRegistered(final int index, final String botType) {
        botManager.ensureBotRegistered(index, () -> initBot(index, botType));
    }

    public void retireBot(final int index) {
        botManager.retireBot(index);
    }

    protected abstract Bot initBot(final int index, final String botType);
}
