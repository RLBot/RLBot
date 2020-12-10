package rlbot;

import rlbot.manager.BotManager;
import rlbot.manager.BotManagerSocket;
import rlbot.pyinterop.SocketServer;

/**
 * See JavaAgent.py for usage instructions
 */
public class JavaExample {

    public static void main(String[] args) {

        if (args.length < 1) {
            throw new IllegalArgumentException("You must pass in a port as an argument!");
        }

        int pythonInteropPort = Integer.parseInt(args[0]); // 24008 currently set in python
        BotManager flatBotManager = new BotManagerSocket();
        flatBotManager.setRefreshRate(120);

        SocketServer server = new SamplePythonInterface(pythonInteropPort, flatBotManager);
        server.start();
    }
}
