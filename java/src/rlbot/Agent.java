package rlbot;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class Agent {

    private Map<String, Bot> bots = new HashMap<>();

    public Agent() {
        bots.put("blue", new Bot(Bot.Team.BLUE));
        bots.put("orange", new Bot(Bot.Team.ORANGE));
    }


    public int[] getOutputVector(ArrayList<ArrayList<Double>> input, String team) {

        AgentInput translatedInput = new AgentInput(input);

        Bot bot = bots.get(team);
        AgentOutput output = bot.getOutput(translatedInput);
        int[] outputForPython = output.toPython();
        return outputForPython;
    }
}
