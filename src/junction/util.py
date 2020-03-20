from typing import Callable, TypeVar, Iterable, Any

from collections import OrderedDict
from collections.abc import Mapping

T = TypeVar("T")


class JunctionError(Exception):
    pass


def for_all(items: Iterable[T], action: Callable[[T], None]) -> None:
    """Runs a particular function for every item in a list.

    Arguments:
        items {List[T]} -- A list of items.
        action {Callable[[T], None]} -- A function to call which accepts a single item.
    """
    for item in items:
        action(item)


class DotDict(OrderedDict):
    """
    Quick and dirty implementation of a dot-able dict, which allows access and
    assignment via object properties rather than dict indexing.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        # we could just call super(DotDict, self).__init__(*args, **kwargs)
        # but that won't get us nested dotdict objects
        od = OrderedDict(*args, **kwargs)
        for key, val in od.items():
            if isinstance(val, Mapping):
                value = DotDict(val)
            else:
                value = val
            self[key] = value

    def __delattr__(self, name: Any) -> None:
        try:
            del self[name]
        except KeyError as ex:
            raise AttributeError(f"No attribute called: {name}") from ex

    def __getattr__(self, k: Any) -> Any:
        try:
            return self[k]
        except KeyError as ex:
            raise AttributeError(f"No attribute called: {k}") from ex

    __setattr__ = OrderedDict.__setitem__
