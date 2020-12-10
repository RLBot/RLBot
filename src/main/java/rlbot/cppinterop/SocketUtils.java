package rlbot.cppinterop;

import java.io.IOException;
import java.io.InputStream;
import java.util.Optional;

public class SocketUtils {

    public static final boolean USE_LITTLE_ENDIAN = false;

    private static final DataType[] DATA_TYPE_VALUES = DataType.values();

    public static Optional<DataType> dataTypeFromInt(final int type) {
        if (type < 0 || type >= DATA_TYPE_VALUES.length) {
            return Optional.empty();
        }
        return Optional.of(DATA_TYPE_VALUES[type]);
    }

    public static Optional<DataType> readDataType(final InputStream stream) throws IOException {
        return dataTypeFromInt(readTwoByteNum(stream));
    }

    public static int readTwoByteNum(final InputStream stream) throws IOException {
        byte[] bytes = new byte[2];
        if (stream.read(bytes) != bytes.length) {
            throw new IOException("Could not read type bytes");
        }
        int first_byte = bytes[0];
        int second_byte = bytes[1];

        if (USE_LITTLE_ENDIAN)
        {
            return first_byte | second_byte << 8;
        }
        else
        {
            return second_byte | first_byte << 8;
        }
    }
}
