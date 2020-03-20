from typing import Callable, List

DISCRIMINATORS_BY_CLASS = {}


def get_all_subclasses(klass: type) -> List[type]:
    """Fetch all of the subclasses of the specified class.

    Arguments:
        klass {Type} -- The class whose subclasses will be retrieved.

    Returns:
        List[Type] -- All classes that are descendants of klass.
    """
    all_subclasses = []

    for subclass in klass.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def discriminator(matcher: Callable[[dict], bool]) -> Callable[[type], type]:
    """Decorator that marks a subclass with how to discriminate it from other
    subclasses.  The discriminators are actually stored in the subclassing module and looked up
    by class via get_matching_subclass.

    Arguments:
        matcher {Callable[[dict], bool]} -- A function that accepts the raw JSON blob and will return true if the annotated class matches.

    Returns:
        Callable[[type], type] -- Decorator function that records the discriminator but otherwise does not modify the annotated class at all.
    """

    def discriminator_decorator(klass: type) -> type:
        DISCRIMINATORS_BY_CLASS[klass] = matcher
        return klass

    return discriminator_decorator


def get_matching_subclass(klass: type, raw_json_dict: dict) -> type:
    """Finds the subclass of klass that matches the provided raw JSON by looking for
    and checking any registered discriminators (using the @discriminator annotation).

    Returns the "most derived" class that matches i.e. if A -> B -> C and both the discriminators
    for B and C match, then C is returned.

    If multiple discriminators match across the entire class hierarchy, the behavior is undefined.

    Arguments:
        klass {type} -- A class whose subclasses will be searched for a match.
        raw_json_dict {dict} -- JSON object decoded into a dictionary (usually via json.loads)

    Returns:
        type -- The most derived class with a matching discriminator; this ends up being klass if no subclasses match at all.
    """
    # more deeply nested classes are at the end of the list, so we reverse
    # the search for a candidate that way the "most specific" class that matches will get
    # caught first and used instead of a more generic intermediate class.
    for candidate in reversed(get_all_subclasses(klass)):
        if candidate in DISCRIMINATORS_BY_CLASS:
            if DISCRIMINATORS_BY_CLASS[candidate](raw_json_dict):
                return candidate

    return klass
