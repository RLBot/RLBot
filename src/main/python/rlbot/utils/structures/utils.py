class EmptyClass:
    pass


def create_enum_object(list, list_name=None, other_attributes=None, attribute_object=None):
    """
    Creates an enum object + adds other attributes.
    :param list: A string list of enum values in order, The first value gets assigned to zero.
    :param list_name: the name of the list if that is also wanting to be stored
    :param other_attributes:  This is a list of tuples.
        The first item in the tuple is the name of the field, the second is the value
    :param attribute_object: An object we should get values for
    :return:
    """
    result = EmptyClass()
    for i in range(len(list)):
        setattr(result, list[i], i if attribute_object is None else getattr(attribute_object, list[i]))
    if list_name is not None:
        setattr(result, list_name, list)
    if other_attributes is not None:
        for attribute_tuple in other_attributes:
            setattr(result, attribute_tuple[0], attribute_tuple[1])
    return result
