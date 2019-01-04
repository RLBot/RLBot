import ctypes


class Struct(ctypes.Structure):
    """
    This class exists to add common python functionality to ctypes.Structure.
    This includes:
        Value equality via the `==` operator.
        Showing contents in `repr(struct)`.
    """

    def __eq__(self, other):
        """
        Note: if your Struct contains pointers, pointer equality is used
        as opposed to following the value at the pointer.
        """
        if type(self) != type(other):
            return False
        for field_name, field_type in self._fields_:
            if getattr(self, field_name) != getattr(other, field_name):
                return False
        return True

    def __repr__(self):
        fields_string = ', '.join(
            f'{field_name}: {repr(getattr(self, field_name))}'
            for field_name, field_type in self._fields_
        )
        return f'{self.__class__.__name__}<{fields_string}>'
