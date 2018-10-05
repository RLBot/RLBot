package rlbot.pyinterop;

import rlbot.Bot;
import rlbot.cppinterop.RLBotDll;
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
        System.out.println("Shutting down...");
        botManager.shutDown();
        try {
            Thread.sleep(1500); // Wait for the bots to finish up
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.exit(0);
    }

    public void ensureBotRegistered(final int index, final String botType, final int team) {
        botManager.ensureBotRegistered(index, () -> initBot(index, botType, team));
    }

    public void retireBot(final int index) {
        botManager.retireBot(index);
    }

    protected abstract Bot initBot(final int index, final String botType, final int team);
}
