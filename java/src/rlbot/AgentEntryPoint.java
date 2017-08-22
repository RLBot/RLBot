package rlbot;

import py4j.GatewayServer;

public class AgentEntryPoint {

    private Agent agent;

    public AgentEntryPoint() {
        agent = new Agent();
    }

    public Agent getAgent() {
        return agent;
    }

    public static void main(String[] args) {
        GatewayServer gatewayServer = new GatewayServer(new AgentEntryPoint());
        gatewayServer.start();
        System.out.println("Gateway server started. Listening for Rocket League data!");
    }

}
