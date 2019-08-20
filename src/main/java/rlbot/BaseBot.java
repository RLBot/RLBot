package rlbot;

import rlbot.cppinterop.RLBotDll;
import rlbot.cppinterop.RLBotInterfaceException;
import rlbot.flat.QuickChatMessages;

public abstract class BaseBot implements Bot {

    protected final int index;
    protected final int team;
    private int lastMessageId = -1;

    public BaseBot(final int index, final int team) {
        this.index = index;
        this.team = team;
    }

    @Override
    public int getIndex() {
        return index;
    }

    @Override
    public void retire() {
    }

    protected QuickChatMessages receiveQuickChat() throws RLBotInterfaceException {

        QuickChatMessages messages = RLBotDll.receiveQuickChat(index, team, lastMessageId);

        if (messages.messagesLength() > 0) {
            lastMessageId = messages.messages(messages.messagesLength() - 1).messageIndex();
        }

        return messages;
    }
}
