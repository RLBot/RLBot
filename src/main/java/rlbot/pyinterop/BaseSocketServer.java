package rlbot.pyinterop;

import rlbot.Bot;
import rlbot.cppinterop.RLBotDll;
import rlbot.manager.BotManager;
import rlbot.manager.IBotManager;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * Listens for signals from the central RLBot framework which runs on python.
 */
public abstract class BaseSocketServer implements PythonInterface {

    private final Integer port;
    protected final IBotManager botManager;

    public BaseSocketServer(final Integer port, IBotManager botManager) {
        this.port = port;
        this.botManager = botManager;
    }

    public void start() {

        System.out.println(String.format("Listening for clients on 127.0.0.1 on port %s...", port));

        try (ServerSocket serverSocket = new ServerSocket(port)) {
            while (true) {
                try (Socket clientSocket = serverSocket.accept()) {
                    byte[] buffer = new byte[clientSocket.getReceiveBufferSize()];
                    int bytes = clientSocket.getInputStream().read(buffer);
                    String request = new String(buffer, 0, bytes);
                    Command command = parseCommand(request);
                    if (command.action == Command.Action.ADD) {
                        ensureStarted(command.dllDirectory);
                        ensureBotRegistered(command.index, command.name, command.team);
                    } else if (command.action == Command.Action.REMOVE) {
                        retireBot(command.index);
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static Command parseCommand(final String socketCommand) {
        String[] split = socketCommand.split("\n");

        if (split.length < 2) {
            throw new IllegalArgumentException("Server received too few command arguments from client");
        }

        Command command = new Command();

        if ("add".equals(split[0])) {
            command.action = Command.Action.ADD;
            command.name = split[1];
            command.team = Integer.parseInt(split[2]);
            command.index = Integer.parseInt(split[3]);
            command.dllDirectory = split[4];
        }
        else if ("remove".equals(split[0])) {
            command.action = Command.Action.REMOVE;
            command.index = Integer.parseInt(split[1]);
        } else {
            throw new IllegalArgumentException("Invalid command: " + split[0]);
        }

        return command;
    }

    protected void ensureStarted(final String interfaceDllPath) {
        try {
            RLBotDll.initialize(interfaceDllPath);
            botManager.ensureStarted();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    protected void shutdown() {
        System.out.println("Shutting down...");
        botManager.shutDown();
        try {
            Thread.sleep(1500); // Wait for the bots to finish up
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.exit(0);
    }

    protected abstract void ensureBotRegistered(final int index, final String botType, final int team);

    protected void retireBot(final int index) {
        botManager.retireBot(index);
        if (botManager.getRunningBotIndices().isEmpty()) {
            shutdown();
        }
    }
}
