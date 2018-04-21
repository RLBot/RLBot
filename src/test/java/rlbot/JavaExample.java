package rlbot;

import rlbot.manager.BotManager;
import rlbot.py.PythonInterface;
import rlbot.py.PythonServer;

/**
 * See JavaAgent.py for usage instructions
 */
public class JavaExample {

    public static void main(String[] args) {

        BotManager botManager = new BotManager();
        PythonInterface pythonInterface = new SamplePythonInterface(botManager);
        Integer port = 45021;
        PythonServer pythonServer = new PythonServer(pythonInterface, port);
        pythonServer.start();
    }
}