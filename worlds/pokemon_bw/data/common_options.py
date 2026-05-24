import random
from typing import Iterable, Dict, Any

from BaseClasses import PlandoOptions
from Options import OptionSet, OptionError, OptionCounter, FreezeValidKeys
from worlds.AutoWorld import World


class AssembleToggles(FreezeValidKeys):

    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]):
        toggles: list[tuple[str, tuple[bool, str] | bool]] = [(key[3:], value) for key, value in attrs.items()
                                                              if key.startswith("is_")]
        for i in range(len(toggles)):
            if not isinstance(toggles[i][1], tuple):
                toggles[i] = toggles[i][0], (toggles[i][1], toggles[i][0].replace("_", " ").capitalize())
        toggles: list[tuple[str, tuple[bool, str]]]
        attrs["_toggles"] = toggles
        attrs["valid_keys"] = attrs["valid_keys"] if "valid_keys" in attrs else []
        attrs["default"] = attrs["default"] if "default" in attrs and isinstance(attrs["default"], list) else []
        for key, data in toggles:
            if data[1] not in attrs["valid_keys"]:
                attrs["valid_keys"].append(data[1])
            if data[0] and data[1] not in attrs["default"]:
                attrs["default"].append(data[1])
        cls = super().__new__(mcs, name, bases, attrs)
        return cls


class ToggleSet(OptionSet, metaclass=AssembleToggles):
    valid_keys_casefold = True
    auto_add_if_any: str | None = None
    _toggles: list[tuple[str, tuple[bool, str]]]
    aliases_convert: list[tuple[str, str]] = []
    ignore_deprecated: list[str] = []

    def __init__(self, value: Iterable[str]):
        super().__init__(value)
        self.value: set[str] = set(val.casefold() for val in value)
        for alias, actual in self.aliases_convert:
            if alias.casefold() in self.value:
                self.value.add(actual.casefold())
                self.value.remove(alias.casefold())
        for to_ignore in self.ignore_deprecated:
            if to_ignore.casefold() in self.value:
                self.value.remove(to_ignore.casefold())
        if self.auto_add_if_any is not None and len(self.value) and self.auto_add_if_any.casefold() not in self:
            self.value.add(self.auto_add_if_any.casefold())
        for key, data in self._toggles:
            setattr(self, "is_"+key, data[1].casefold() in self.value)

    def __contains__(self, item: str):
        return item.casefold() in self.value

    def verify_keys(self) -> None:
        if self.valid_keys:
            dataset = set(word.casefold() for word in self.value)
            extra = dataset - set(key.casefold() for key in self._valid_keys)
            if extra:
                raise OptionError(
                    f"Found unexpected key {', '.join(extra)} in {getattr(self, 'display_name', self)}. "
                    f"Allowed keys: {self._valid_keys}."
                )


class ExtendedOptionCounter(OptionCounter):
    value: dict[str, int]
    individual_min_max: dict[str, tuple[int, int]] = {}
    min_max_pairs: list[tuple[str, str]] = []
    fill_defaults: bool = False

    @classmethod
    def from_any(cls, data: Dict[str, Any]):
        data = data.copy()
        if not isinstance(data, dict):
            raise NotImplementedError(f"Cannot Convert from non-dictionary, got {type(data)}")
        if cls.fill_defaults:
            for key in cls.valid_keys:
                if key not in data:
                    if key in cls.default:
                        data[key] = cls.default[key]
                    else:
                        data[key] = 0
                data[key] = cls.resolve_value(data[key], key)
        return cls(data)

    def verify(self, world: type[World], player_name: str, plando_options: PlandoOptions) -> None:
        super().verify(world, player_name, plando_options)

        errors = []

        for key in self.value:
            if key in self.individual_min_max:
                _min, _max = self.individual_min_max[key]
                if not _min <= self.value[key] <= _max:
                    errors.append(f"{key}: {self.value[key]} not in range {_min} to {_max}")

        for min_key, max_key in self.min_max_pairs:
            if min_key in self.value and max_key in self.value:
                if self.value[min_key] > self.value[max_key]:
                    errors.append(f"{min_key} is higher than {max_key}")

        if len(errors) != 0:
            errors = [f"For option {getattr(self, 'display_name', self)} of player {player_name}:"] + errors
            raise OptionError("\n".join(errors))

    @classmethod
    def resolve_value(cls, val: int | dict[Any, int] | list | str, key: str) -> int:
        if isinstance(val, int):
            return val
        elif isinstance(val, list):
            return cls.resolve_value(random.choice(val), key)
        elif isinstance(val, dict):
            return cls.resolve_value(random.choices(list(val.keys()), list(val.values())), key)
        elif isinstance(val, str) and val.startswith("random"):
            if val == "random":
                return random.randint(*(cls.individual_min_max[key]))
            elif val.startswith("random-range-"):
                parts = val.split("-")
                if parts[-2].isnumeric() and parts[-1].isnumeric():
                    start = int(parts[-2])
                    end = int(parts[-1])
                    _min, _max = cls.individual_min_max[key]
                    if _min <= start <= _max and _min <= end <= _max and start <= end:
                        return random.randint(start, end)
        raise OptionError(
            f"Invalid value \"{val}\" for key \"{key}\" in option \"{getattr(cls, 'display_name', cls)}\"."
        )
