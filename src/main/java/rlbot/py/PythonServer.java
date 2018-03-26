package rlbot.py;

import py4j.GatewayServer;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;
import java.util.stream.Stream;

public class PythonServer {

    private final Object pythonInterface;
    private final Integer port;

    public PythonServer(PythonInterface pythonInterface, Integer port) {
        this.pythonInterface = pythonInterface;
        this.port = port;
    }

    public void start() {
        GatewayServer gatewayServer = new GatewayServer(pythonInterface, port);
        gatewayServer.start();
        System.out.println(String.format("Gateway server started on port %s. Listening for commands!", port));
    }
}
