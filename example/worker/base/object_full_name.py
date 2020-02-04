def object_full_name(item):
    """
    Return the object's class full name, including module.

    Taken from https://stackoverflow.com/questions/37568128/
                       get-fully-qualified-name-of-a-python-class-python-3-3

    with, of course, changes.

    :param item: The class or instance of the class.
    :return: A string representation of the class full name.
    """
    try:
        qual_name = item.__qualname__
    except AttributeError:
        qual_name = item.__class__.__qualname__
    return item.__module__ + '.' + qual_name
