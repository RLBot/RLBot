package rlbot;

import rlbot.manager.BotManager;
import rlbot.manager.FlatBotManager;
import rlbot.py.DefaultPythonInterface;

public class SamplePythonInterface extends DefaultPythonInterface {

    private FlatBotManager flatBotManager;

    public SamplePythonInterface(BotManager botManager, FlatBotManager flatBotManager) {
        super(botManager);

        this.flatBotManager = flatBotManager;
    }

    @Override
    protected ProtobufBot initBot(int index, String botType, int team) {
        return new ProtobufBot(index);
    }

    public void ensureStarted() {
        super.ensureStarted();
        flatBotManager.ensureStarted();
    }

    public void ensureFlatBotRegistered(final int index, final String botType, final int team) {
        flatBotManager.ensureBotRegistered(index, () -> initFlatBot(index, botType, team));
    }

    protected FlatBot initFlatBot(int index, String botType, int team) {
        return new FlatbufferBot(index);
    }
}
