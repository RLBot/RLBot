package rlbot;

import rlbot.manager.BotManager;
import rlbot.pyinterop.DefaultPythonInterface;

public class SamplePythonInterface extends DefaultPythonInterface {

    public SamplePythonInterface(BotManager botManager) {
        super(botManager);
    }

    protected Bot initBot(int index, String botType, int team) {
        return new SampleBot(index);
    }
}
