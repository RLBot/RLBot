package rlbot;

import rlbot.flat.GameTickPacket;

/**
 * All java bots must implement this interface, mainly so that the {@link rlbot.manager.BotManager} will
 * be able to handle them properly.
 */
public interface Bot {

    /**
     * Returns the index that was used when registering this bot.
     * This is the same as the index referred to in rlbot.cfg.
     */
    int getIndex();

    /**
     * Bot logic goes here. Returns controls based on the information you receive about the game.
     * This is also a good place to enact side effects like rendering, etc.
     */
    ControllerState processInput(GameTickPacket request);

    /**
     * Shuts down the bot and close any resources it's using.
     */
    void retire();
}
