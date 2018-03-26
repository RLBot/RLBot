package rlbot.cpp;

import com.sun.jna.Pointer;
import com.sun.jna.Structure;

import java.util.Arrays;
import java.util.List;

public class ByteBufferStruct extends Structure implements Structure.ByValue {

    private static final List<String> fields = Arrays.asList("ptr", "size");

    public Pointer ptr;
    public int size;

    @Override
    protected List<String> getFieldOrder() {
        return fields;
    }
}
