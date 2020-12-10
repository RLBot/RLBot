package rlbot.manager;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.ControllerState;
import rlbot.cppinterop.DataType;
import rlbot.cppinterop.RLBotDll;
import rlbot.cppinterop.SocketUtils;
import rlbot.flat.FieldInfo;
import rlbot.flat.GameTickPacket;
import rlbot.flatutil.GameTickPacketWrapper;

import java.io.IOException;
import java.net.Socket;
import java.nio.ByteBuffer;

/**
 * This class keeps track of all the bots, runs the main logic loops, and retrieves the
 * game data on behalf of the bots.
 */
public class BotManagerSocket extends BotManager {

    private String host;
    private int port;

    private Socket socket;

    private GameTickPacketWrapper packetWrapper;

    @Override
    public void setSocketInfo(String socketHost, int socketPort) {
        this.host = socketHost;
        this.port = socketPort;
    }

    public void ensureStarted() {
        if (keepRunning) {
            return; // Already started
        }

        keepRunning = true;
        Thread looper = new Thread(this::doLoop);
        looper.start();
    }

    private void doLoop() {

        try {
            // TODO: make this connection retry
            socket = new Socket(host, port);
            while (keepRunning) {
                try {
                    readMessage(socket);
                } catch (IOException e) {
                    e.printStackTrace();
                    socket = new Socket(host, port);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    private void readMessage(Socket socket) throws IOException {
        DataType type = SocketUtils.readDataType(socket.getInputStream()).orElseThrow(() -> new IOException("Failed to parse data type!"));
        int size = SocketUtils.readTwoByteNum(socket.getInputStream());

        byte[] payload = new byte[size];
        if (socket.getInputStream().read(payload) != payload.length) {
            throw new IOException("Failed to read entire payload.");
        }

        switch (type) {
            case live_data_packet:
                packetWrapper = new GameTickPacketWrapper(payload);
                latestPacket = packetWrapper.gameTickPacket;

                System.out.println("Seconds elapsed: " + latestPacket.gameInfo().secondsElapsed());
                synchronized (dinnerBell) {
                    dinnerBell.notifyAll();
                }

                break;
            case field_info_packet:
                RLBotDataCache.fieldInfo = FieldInfo.getRootAsFieldInfo(ByteBuffer.wrap(payload));
            default:
                System.out.println(String.format("Ignored message type %s", type.name()));
        }
    }

    @Override
    protected void sendControllerState(ControllerState controllerState, int playerIndex) {
        FlatBufferBuilder builder = RLBotDll.controllerStateToFlatbuffer(controllerState, playerIndex);
        try {
            socket.getOutputStream().write(builder.sizedByteArray());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
