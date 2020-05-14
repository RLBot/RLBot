package rlbot.manager;

import rlbot.ControllerState;
import rlbot.Hivemind;
import rlbot.cppinterop.RLBotDll;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Function;

/**
 * This class is a BotManager for hiveminds. It runs the main logic loops and retrieves GameTickPackets for
 * the hiveminds.
 */
public class HivemindManager extends BaseBotManager {

    // There are only ever two hiveminds of this bot, one for each team.
    private final HivemindProcess[] hivemindProcesses = new HivemindProcess[2];
    private final Function<Integer, Hivemind> hivemindSupplier;

    public HivemindManager(Function<Integer, Hivemind> hivemindSupplier) {
        this.hivemindSupplier = hivemindSupplier;
    }

    public void ensureBotRegistered(int index, int team) {
        if (hivemindProcesses[team] == null || !hivemindProcesses[team].isRunning()) {
            // Start a new instance of the hivemind
            Hivemind hivemind = hivemindSupplier.apply(team);
            final AtomicBoolean runFlag = new AtomicBoolean(true);
            Thread hiveTread = new Thread(() -> doHiveLoop(hivemind, team, runFlag));
            hiveTread.start();
            hivemindProcesses[team] = new HivemindProcess(hiveTread, runFlag);
        }

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

                    Set<Integer> droneIndices = hivemindProcesses[team].getDroneIndices();
                    if (droneIndices.isEmpty()) continue;
                    Map<Integer, ControllerState> hivemindOutput = hivemind.processInput(droneIndices, latestPacket);

                    if (droneIndices.size() > hivemindOutput.size())
                        System.out.println("Not enough outputs were given.");
                    else if (droneIndices.size() < hivemindOutput.size())
                        System.out.println("Too many inputs were given.");

                    for (Integer index : hivemindOutput.keySet()) {
                        if (!droneIndices.contains(index)) {
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
        HashSet<Integer> allIndices = new HashSet<>();
        if (hivemindProcesses[0] != null && hivemindProcesses[0].isRunning()) allIndices.addAll(hivemindProcesses[0].getDroneIndices());
        if (hivemindProcesses[1] != null && hivemindProcesses[1].isRunning()) allIndices.addAll(hivemindProcesses[1].getDroneIndices());
        return allIndices;
    }

    /**
     * Returns a set of every blue bot index that is currently registered and running in this java process.
     * Will not include indices from humans, bots in other languages, or bots in other java processes.
     *
     * This may be useful for driving a basic status display.
     */
    public Set<Integer> getRunningBotIndicesForBlue() {
        if (hivemindProcesses[0] != null && hivemindProcesses[0].isRunning()) {
            return hivemindProcesses[0].getDroneIndices();
        }
        return new HashSet<>();
    }

    /**
     * Returns a set of every orange bot index that is currently registered and running in this java process.
     * Will not include indices from humans, bots in other languages, or bots in other java processes.
     *
     * This may be useful for driving a basic status display.
     */
    public Set<Integer> getRunningBotIndicesForOrange() {
        if (hivemindProcesses[1] != null && hivemindProcesses[1].isRunning()) {
            return hivemindProcesses[1].getDroneIndices();
        }
        return new HashSet<>();
    }

    @Override
    public void retireBot(int index) {
        if (hivemindProcesses[0] != null) hivemindProcesses[0].retireDrone(index);
        if (hivemindProcesses[1] != null) hivemindProcesses[1].retireDrone(index);
    }

    public void retireHivemind(int team) {
        hivemindProcesses[team].stop();
    }
}
