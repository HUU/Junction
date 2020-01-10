import json
from collections.abc import Mapping, Iterable
from typing import get_type_hints, get_origin, get_args

from junction.__util import DotDict
from junction.confluence.models import ApiModel

class ApiEncoder(json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, 'encode_json'):
            return obj.encode_json()

        return super().default(obj)

def ApiDecoder(root_klass):
    class KlassJSONDecoder(object):
        def decode(self, s):
            raw_dict = json.loads(s)
            return self.__marshal_to_class(raw_dict, root_klass)

        def __marshal_to_class(self, dict, klass):
            new_obj = klass()
            hints = get_type_hints(klass)
            for key, value in dict.items():
                if hasattr(new_obj, key):
                    if key not in hints:
                        setattr(new_obj, key, value if not issubclass(value.__class__, Mapping) else DotDict(value))
                    else:
                        setattr(new_obj, key, self.__marshal_hinted_class(value, hints[key]))
            return new_obj

        def __marshal_hinted_class(self, value, hint):
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

    return KlassJSONDecoder