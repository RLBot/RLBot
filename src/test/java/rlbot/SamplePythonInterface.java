package rlbot;

import rlbot.manager.BotManager;
import rlbot.py.DefaultPythonInterface;
import rlbot.py.PythonInterface;

public class SamplePythonInterface extends DefaultPythonInterface {

    public SamplePythonInterface(BotManager botManager) {
        super(botManager);
    }

    @Override
    protected Bot initBot(int index, String botType) {
        return new SampleBot(index);
    }
}
