package rlbot.manager;

import com.google.protobuf.InvalidProtocolBufferException;
import rlbot.Bot;
import rlbot.api.GameData;
import rlbot.cpp.RLBotDll;

import java.util.HashMap;
import java.util.Map;

public class BotManager {

    private final Map<Integer, BotProcess> botProcesses = new HashMap<>();

    private boolean keepRunning;

    private final Object dinnerBell = new Object();
    private  GameData.GameTickPacket latestPacket;

    public void registerBot(final int index, final Bot bot) {
        if (botProcesses.containsKey(index)) {
            return;
        }

        botProcesses.computeIfAbsent(index, (idx) -> {
            Thread botThread = new Thread(() -> doRunBot(bot));
            botThread.start();
            return new BotProcess(bot, botThread);
        });
    }

    private void doRunBot(Bot bot) {
        while (keepRunning) {
            try {
                synchronized (dinnerBell) {
                    dinnerBell.wait(1000);
                }
                GameData.ControllerState controllerState = bot.processInput(latestPacket);
                RLBotDll.setControllerState(controllerState, bot.getIndex());
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        bot.retire();
    }

    private void retireBots() {
        botProcesses.clear();
    }

    public void start() {
        if (keepRunning) {
            return; // Already started
        }

        keepRunning = true;
        Thread looper = new Thread(this::doLoop);
        looper.start();
    }

    private void doLoop() {
        while (keepRunning) {

            try {
                latestPacket = RLBotDll.getProtoPacket();
                synchronized (dinnerBell) {
                    dinnerBell.notifyAll();
                }

            } catch (InvalidProtocolBufferException e) {
                e.printStackTrace();
            }

            try {
                Thread.sleep(16);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }
    }

    public void retire() {
        keepRunning = false;
        retireBots();
    }
}
