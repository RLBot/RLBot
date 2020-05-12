package rlbot;

import rlbot.manager.BotManager;
import rlbot.manager.HivemindManager;
import rlbot.pyinterop.HiveSocketServer;
import rlbot.pyinterop.SocketServer;

/**
 * See JavaAgent.py for usage instructions
 */
public class JavaExample {

    public static void main(String[] args) {

        if (args.length < 1) {
            throw new IllegalArgumentException("You must pass in a port as an argument!");
        }

//        BotManager flatBotManager = new BotManager();
//        flatBotManager.setRefreshRate(120);
//        int port = Integer.parseInt(args[0]);
//        SocketServer server = new SamplePythonInterface(port, flatBotManager);
//        server.start();

        HivemindManager hive = new HivemindManager(() -> new MyHivemind());
        HiveSocketServer server = new HiveSocketServer(port, hive);
        server.start();
    }
}
