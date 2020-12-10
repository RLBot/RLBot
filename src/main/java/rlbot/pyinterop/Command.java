package rlbot.pyinterop;

public class Command {
    Action action;
    int index;
    int team;
    String name;
    String dllDirectory;
    String socketHost; // If we're using RLBot sockets, which port should we connect to
    int socketPort; // If we're using RLBot sockets, which port should we connect to

    enum Action {
        ADD_DLL_BOT,
        ADD_SOCKET_BOT,
        REMOVE
    }
}
