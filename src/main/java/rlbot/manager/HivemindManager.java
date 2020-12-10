package rlbot.manager;

import rlbot.ControllerState;
import rlbot.Hivemind;
import rlbot.cppinterop.RLBotDll;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Function;

/**
 * This class is a BotManager for hiveminds. It runs the main logic loops and retrieves GameTickPackets for
 * the hiveminds.
 */
public class HivemindManager extends BaseBotManager {

    private final static String BLUE_POSTFIX = " [blue]";
    private final static String ORANGE_POSTFIX = " [orange]";

    // Each hivemind is associated with a hive key. The postfixes "[blue]" or "[orange]" are used
    // to differentiate between teams
    private final Map<String, HivemindProcess> hivemindProcesses = new ConcurrentHashMap<>();
    private final Map<Integer, HivemindProcess> hivemindProcessOfDrone = new ConcurrentHashMap<>();
    private final HivemindCreator hivemindCreator;

    /**
     * Create a HivemindManager, that only administrates one hivemind per team. Their hive key will be "Default".
     */
    public HivemindManager(Function<Integer, Hivemind> hivemindSupplier) {
        hivemindCreator = new HivemindCreator() {
            @Override
            public Hivemind createHivemind(int team, String hiveKey) {
                return hivemindSupplier.apply(team);
            }

            @Override
            public String assignHiveKey(int index, int team, String botName) {
                // No HivemindCreator provided, so the key will just be "Default"
                return "Default";
            }
        };
    }

    /**
     * Create a HivemindManager able to manage multiple hiveminds. Each hivemind is associated with a hive key,
     * which is assigned to newly registered bots by the given HivemindCreator.
     */
    public HivemindManager(HivemindCreator hivemindCreator) {
        this.hivemindCreator = hivemindCreator;
    }

    public void ensureBotRegistered(int index, int team, String botName) {

        // Is this drone already registered somewhere?
        if (hivemindProcessOfDrone.containsKey(index)) {
            return;
        }

        String hiveKey = hivemindCreator.assignHiveKey(index, team, botName);
        String coloredHiveKey = hiveKey + (team == 0 ? BLUE_POSTFIX : ORANGE_POSTFIX);

        HivemindProcess hivemindProcess = hivemindProcesses.computeIfAbsent(coloredHiveKey, (nhk) -> {
            // Start a new instance of the hivemind
            Hivemind hivemind = hivemindCreator.createHivemind(team, hiveKey);
            final AtomicBoolean runFlag = new AtomicBoolean(true);
            Thread hiveTread = new Thread(() -> doHiveLoop(hivemind, coloredHiveKey, team, runFlag));
            hiveTread.start();
            return new HivemindProcess(hiveTread, runFlag, coloredHiveKey);
        });

        hivemindProcess.registerDrone(index);
        hivemindProcessOfDrone.put(index, hivemindProcess);
    }

    private void doHiveLoop(Hivemind hivemind, final String coloredHiveKey, final int team, final AtomicBoolean runFlag) {

        try {
            while (keepRunning && runFlag.get()) {

                synchronized (dinnerBell) {
                    // Wait for the main thread to indicate that we have new game tick data.
                    dinnerBell.wait(1000);
                }
                if (latestPacket != null) {

                    Set<Integer> droneIndices = hivemindProcesses.get(coloredHiveKey).getDroneIndices();
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
            retireHivemind(coloredHiveKey); // Unregister this hivemind internally.
            hivemind.retire(); // Tell the hivemind to clean up its resources.
        }
    }

    @Override
    public Set<Integer> getRunningBotIndices() {
        return hivemindProcessOfDrone.keySet();
    }

    /**
     * Returns a set of every bot index that is currently registered and running for the give hive and team.
     * Will not include indices from humans, bots in other languages, or bots in other java processes.
     *
     * This may be useful for driving a basic status display.
     */
    public Set<Integer> getRunningBotIndices(int team, String hiveKey) {
        String coloredHiveKey = hiveKey + (team == 0 ? BLUE_POSTFIX : ORANGE_POSTFIX);
        HivemindProcess hivemindProcess = hivemindProcesses.get(coloredHiveKey);
        if (hivemindProcess == null) return new HashSet<>();
        return hivemindProcess.getDroneIndices();
    }

    @Override
    public void retireBot(int index) {
        HivemindProcess hivemindProcess = hivemindProcessOfDrone.get(index);
        if (hivemindProcess != null) {
            hivemindProcess.retireDrone(index);
            hivemindProcessOfDrone.remove(index);
            // If the hive is now empty, we will retire it
            if (hivemindProcess.getDroneIndices().isEmpty()) {
                retireHivemind(hivemindProcess.getHiveKey());
            }
        }
    }

    @Override
    public void setSocketInfo(String socketHost, int socketPort) {
        // TODO: implement
    }

    /**
     * Stop the hivemind process with the given coloredHiveKey (with team postfix) and unregister the drones indices.
     */
    public void retireHivemind(String coloredHiveKey) {
        HivemindProcess hivemindProcess = hivemindProcesses.get(coloredHiveKey);
        if (hivemindProcess != null) {
            hivemindProcess.stop();
            for (int index : hivemindProcess.getDroneIndices()) {
                hivemindProcessOfDrone.remove(index);
            }
        }
    }
}
