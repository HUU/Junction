import json
from collections.abc import Mapping, Iterable
from typing import (
    get_type_hints,
    get_origin,
    get_args,
    Type,
    Any,
    Union,
    Generic,
    TypeVar,
    cast,
)

from junction.util import DotDict
from junction.confluence.models import ApiModel
from junction.confluence.models.subclassing import get_matching_subclass


NoneType = type(None)


class ApiEncoder(json.JSONEncoder):
    """A JSON encoder that pairs well with ApiModel.  Uses the "default" encoder unless the object
    implements an encode_json method.  If so, the object returned by encode_json is encoded instead.
    In most cases this is just self.__dict__.
    """

    def default(self, obj: Any) -> Any:
        if hasattr(obj, "encode_json"):
            return obj.encode_json()

        return super().default(obj)


T = TypeVar("T", bound=ApiModel)


class ApiDecoder(Generic[T]):
    def __init__(self, root_klass: Type[T]):
        """A JSON decoder that pairs well with a particular ApiModel.  The resulting decoder can
        decode JSON that matches the format of root_klass or any of its subclasses (annotated with @discriminator's).

        The decoder relies on type hints to figure out what each member should be interpreted as.  If the decoder encounters
        any types it does not understand or members without type hints, it will deserialize them as DotDict's to maintain
        dot accessor compatibility for all members.

        Arguments:
            root_klass {type} -- The type we expect to be decoding with this decoder.

        Returns:
            An instance of a custom decoder class that works with this particular type.
        """
        self.root_klass = root_klass

    def decode(self, s: str) -> T:
        """Decodes a given JSON blob (encoded as a string) into a particular class.  Does this by first
        reading the entire JSON blob into  dictionary and then recursively marshaling the members to the
        appropriate classes by using the type hints on the target class.

        Only supports type hints that are ApiModel subclasses, non-collection primitives, and List[T] of the above.

        Arguments:
            s {str} -- A JSON object encoded as a string.

        Returns:
            An instance of root_klass with members filled in and strongly typed based on type hints.
        """
        raw_dict = json.loads(s)
        return self.__marshal_to_class(raw_dict, self.root_klass)

    def __marshal_to_class(self, dict: dict, klass: Type[ApiModel]) -> T:
        target_klass = cast(
            Type[ApiModel],
            (
                get_origin(klass)
                if get_origin(klass)
                and issubclass(cast(type, get_origin(klass)), ApiModel)
                else klass
            ),
        )  # unwrap Generics
        new_obj = get_matching_subclass(target_klass, dict)()
        hints = get_type_hints(target_klass)
        for key, value in dict.items():
            if hasattr(new_obj, key):
                if key not in hints:
                    setattr(
                        new_obj,
                        key,
                        value
                        if not issubclass(value.__class__, Mapping)
                        else DotDict(value),
                    )
                else:
                    setattr(
                        new_obj, key, self.__marshal_hinted_class(value, hints[key])
                    )
        return new_obj

    def __marshal_hinted_class(self, value: Any, hint: Any) -> Any:
        if get_origin(hint) is Union and (hint_args := get_args(hint))[1] is NoneType:  # type: ignore
            # this is an Optional[T]..unwrap the real type:
            hint = hint_args[0]
        elif hasattr(hint, "__bound__"):
            # this is a TypeVar (probably from a generic), fetch the type binding information
            hint = hint.__bound__

        if get_origin(hint) is list and issubclass(value.__class__, Iterable):
            list_item_hint = get_args(hint)[0]
            return [self.__marshal_hinted_class(x, list_item_hint) for x in value]
        elif isinstance(hint, type) and issubclass(hint, ApiModel):
            return self.__marshal_to_class(value, hint)
        else:
            # don't know what this is or don't support it so
            # just bring it back as a dotdict and we might get
            # lucky
            return DotDict(value) if issubclass(value.__class__, Mapping) else value
