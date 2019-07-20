package rlbot.cppinterop;

import java.io.IOException;

/**
 * A problem encountered when reading or writing data via the RLBot interface.
 */
public class RLBotInterfaceException extends IOException {
    public RLBotInterfaceException(String message) {
        super(message);
    }

    public RLBotInterfaceException(String message, Throwable cause) {
        super(message, cause);
    }

    public RLBotInterfaceException(Throwable error) {
        super(error);
    }
}
