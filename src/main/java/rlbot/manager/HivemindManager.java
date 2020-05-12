package rlbot.manager;

import rlbot.ControllerState;
import rlbot.Hivemind;
import rlbot.cppinterop.RLBotDll;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Supplier;

public class HivemindManager extends BaseBotManager {

    private final HivemindProcess[] hivemindProcesses = new HivemindProcess[2];

    public HivemindManager(Supplier<Hivemind> hivemindSupplier) {
        // Setup two hivemind processes. One for each team
        for (int i = 0; i < 2; i++) {
            final int team = i;
            Hivemind hivemind = hivemindSupplier.get();
            final AtomicBoolean runFlag = new AtomicBoolean(true);
            Thread hiveTread = new Thread(() -> doHiveLoop(hivemind, team, runFlag));
            hiveTread.start();
            hivemindProcesses[i] = new HivemindProcess(hiveTread, runFlag);
        }
    }

    public void ensureBotRegistered(int index, int team) {
        hivemindProcesses[team].registerDrone(index);
    }

    private void doHiveLoop(Hivemind hivemind, final int team, final AtomicBoolean runFlag) {

        try {
            while (keepRunning && runFlag.get()) {

                synchronized (dinnerBell) {
                    // Wait for the main thread to indicate that we have new game tick data.
                    dinnerBell.wait(1000);
                }
                if (latestPacket != null) {

                    Set<Integer> droneIndexes = hivemindProcesses[team].getDroneIndexes();
                    if (droneIndexes.isEmpty()) continue;
                    Map<Integer, ControllerState> hivemindOutput = hivemind.processInput(droneIndexes, latestPacket);

                    if (droneIndexes.size() > hivemindOutput.size())
                        System.out.println("Not enough outputs were given.");
                    else if (droneIndexes.size() < hivemindOutput.size())
                        System.out.println("Too many inputs were given.");

                    for (Integer index : hivemindOutput.keySet()) {
                        if (!droneIndexes.contains(index)) {
                            System.out.println("Tried to send output for a bot index (" + index + ") that is not part of the hivemind");
                            continue;
                        }
                        ControllerState output = hivemindOutput.get(index);
                        RLBotDll.setPlayerInputFlatbuffer(output, index);
                    }
                }
            }
        } catch (Exception e) {
            System.out.println("Hive died because an exception occurred in the run loop!");
            e.printStackTrace();
        } finally {
            retireHivemind(team); // Unregister this hivemind internally.
            hivemind.retire(); // Tell the hivemind to clean up its resources.
        }
    }

    @Override
    public Set<Integer> getRunningBotIndices() {
        Set<Integer> blueIndexes = hivemindProcesses[0].getDroneIndexes();
        Set<Integer> orangeIndexes = hivemindProcesses[1].getDroneIndexes();

        HashSet<Integer> allIndexes = new HashSet<>(blueIndexes);
        allIndexes.addAll(orangeIndexes);
        return allIndexes;
    }

    @Override
    public void retireBot(int index) {
        hivemindProcesses[0].retireDrone(index);
        hivemindProcesses[1].retireDrone(index);
    }

    public void retireHivemind(int team) {
        hivemindProcesses[team].stop();
    }
}
