package rlbot.input;

import rlbot.cppinterop.RLBotDll;
import rlbot.flat.FieldInfo;
import rlbot.flat.GameTickPacket;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class FieldInfoManager {
    private List<DropshotTile> dropshotTiles = new ArrayList<>();

    public List<DropshotTile> getDropshotTiles() {
        return dropshotTiles;
    }

    public void addPacketInfo(GameTickPacket packet) {
        if (packet.tileInformationLength() > dropshotTiles.size()) {
            initDropshotTiles();
        }

        for (int i = 0; i < packet.tileInformationLength() && i < dropshotTiles.size(); i++) {
            dropshotTiles.get(i).setState(packet.tileInformation(i));
        }
    }

    private void initDropshotTiles() {
        try {
            FieldInfo fieldInfo = RLBotDll.getFieldInfo();
            dropshotTiles.clear();
            for (int i = 0; i < fieldInfo.goalsLength(); i++) {
                dropshotTiles.add(new DropshotTile(fieldInfo.goals(i)));
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}
