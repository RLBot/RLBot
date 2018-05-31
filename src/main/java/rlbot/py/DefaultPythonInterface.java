package rlbot.py;

import rlbot.Bot;
import rlbot.cpp.RLBotDll;
import rlbot.manager.BotManager;

import java.io.IOException;

/**
 * The public methods of this class will be called directly from the python component of the RLBot framework.
 */
public abstract class DefaultPythonInterface implements PythonInterface {

    private final BotManager botManager;

    public DefaultPythonInterface(BotManager botManager) {
        this.botManager = botManager;
    }

    public void ensureStarted(final String interfaceDllPath) {
        try {
            RLBotDll.initialize(interfaceDllPath);
            botManager.ensureStarted();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void shutdown() {
        botManager.shutDown();
    }

    public void ensureBotRegistered(final int index, final String botType, final int team) {
        botManager.ensureBotRegistered(index, () -> initBot(index, botType, team));
    }

    public void retireBot(final int index) {
        botManager.retireBot(index);
    }

    protected abstract Bot initBot(final int index, final String botType, final int team);
}
