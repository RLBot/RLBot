package rlbot;

import com.google.gson.Gson;
import rlbot.input.PyGameTickPacket;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class Agent {

    private Map<Bot.Team, Bot> bots = new HashMap<>();
    private Gson gson = new Gson();

    public Agent() {
        bots.put(Bot.Team.BLUE, new Bot(Bot.Team.BLUE));
        bots.put(Bot.Team.ORANGE, new Bot(Bot.Team.ORANGE));
    }

    public int[] getOutputVector(String packetJson, String teamString) {

        AgentOutput output;

        try {

            Bot.Team team = Bot.Team.valueOf(teamString.toUpperCase());
            PyGameTickPacket packet = gson.fromJson(packetJson, PyGameTickPacket.class);
            AgentInput translatedInput = new AgentInput(packet, team);

            Bot bot = bots.get(team);
            output = bot.getOutput(translatedInput);

        } catch (Exception e) {
            e.printStackTrace();
            output = new AgentOutput();
        }
        int[] outputForPython = output.toPython();
        return outputForPython;
    }
}
