package rlbot.pyinterop;

public class Command {
    Action action;
    int index;
    int team;
    String name;
    String dllDirectory;

    enum Action {
        ADD,
        REMOVE
    }
}
