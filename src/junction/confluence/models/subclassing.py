from typing import Callable

DISCRIMINATORS_BY_CLASS = {}


def get_all_subclasses(klass):
    all_subclasses = []

    for subclass in klass.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def discriminator(matcher: Callable[[dict], bool]):
    def discriminator_decorator(klass):
        DISCRIMINATORS_BY_CLASS[klass] = matcher
        return klass

    return discriminator_decorator


def get_matching_subclass(klass, raw_json_dict):
    for candidate in get_all_subclasses(klass):
        if candidate in DISCRIMINATORS_BY_CLASS:
            if DISCRIMINATORS_BY_CLASS[candidate](raw_json_dict):
                return candidate

    return klass
