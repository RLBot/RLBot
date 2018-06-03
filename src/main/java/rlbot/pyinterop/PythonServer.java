package rlbot.pyinterop;

import py4j.GatewayServer;

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
