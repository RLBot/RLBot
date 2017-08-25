package rlbot;

import py4j.GatewayServer;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Optional;
import java.util.stream.Stream;

/**
 * See JavaAgent.py for usage instructions
 */
public class AgentEntryPoint {

    // TODO: You need to choose a unique port number for yourself that is unlikely to conflict with other bots! See JavaAgent.py for more details.
    // This should match the port defined in JavaAgent.py
    public static final int PORT = -1;
    private Agent agent;

    public AgentEntryPoint() {
        agent = new Agent();
    }

    public Agent getAgent() {
        return agent;
    }

    public static void main(String[] args) {

        // TODO: remove this once you've chosen a port
        if (PORT < 0) {
            throw new RuntimeException("The person programming this bot (you?) needs to choose a port number! See instructions in JavaAgent.py.");
        }

        // Scenario: you finished your bot and submitted it to a tournament. Your opponent hard-coded the same
        // as you, and the match can't start because of the conflict. Because of this line, you can ask the
        // organizer make a file called "port.txt" in the same directory as your .jar, and put some other number in it.
        // This matches code in JavaAgent.py
        int port = readPortFromFile().orElse(PORT);

        GatewayServer gatewayServer = new GatewayServer(new AgentEntryPoint(), port);
        gatewayServer.start();
        System.out.println(String.format("Gateway server started on port %s. Listening for Rocket League data!", port));
    }

    private static Optional<Integer> readPortFromFile() {
        try {
            Stream<String> lines = Files.lines(Paths.get("port.txt"));
            Optional<String> firstLine = lines.findFirst();
            return firstLine.map(Integer::parseInt);
        } catch (NumberFormatException e) {
            System.out.println("Failed to parse port file! Will proceed with hard-coded port number.");
            return Optional.empty();
        } catch (Throwable e) {
            return Optional.empty();
        }
    }

}
