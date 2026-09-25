import random
from pathlib import Path
from typing import Any, Iterable, Self, Dict

from Options import Range, Toggle, OptionError, Visibility
from ..data.common_options import ExtendedOptionCounter
from ..data.pokemon.pokedex import by_name as dex_by_name
from ..data.pokemon.species import unique_forms
from worlds import world_sources

DEXSANITYSANITY_ENABLED = any(Path(source.path).stem == "pokemon_bw_dexsanitysanity" for source in world_sources)
DEXSANITYSANITY_VISIBILITY = Visibility.spoiler if not DEXSANITYSANITY_ENABLED else Visibility.all


class DexsanityResolver:

    def resolve_plando_dex(self, value: int | str | list | dict) -> tuple[int, ...]:
        while not isinstance(value, int | range):
            if isinstance(value, str):
                if "," in value:
                    value = value.split(",")
                elif "-" in value and all(a.strip().isnumeric() for a in value.split("-")):
                    res = tuple(int(r) for r in value.split("-"))
                    for r in res:
                        if not 1 <= r <= 649:
                            raise OptionError(f"Option {self.__class__.__name__} contains dex number {r}, "
                                              f"which is not in range 1-649")
                    value = range(res[0], res[1] + 1)
                elif value.strip().isnumeric():
                    value = int(value)
                elif res := dex_by_name.get(value, False):
                    value = res
                else:
                    raise OptionError(f"Option {self.__class__.__name__} contains invalid string value {value}")
            elif isinstance(value, list):
                value = random.choice(value)
            elif isinstance(value, dict):
                for v in value.values():
                    if not isinstance(v, int):
                        raise OptionError(f"Option {self.__class__.__name__} contains a list with a non-integer "
                                          f"weight {v} ({type(v)})")
                value = random.choices(tuple(value), tuple(value.values()))
            else:
                raise OptionError(f"Option {self.__class__.__name__} as a list expects integers, ranges, "
                                  f"nested lists, and nested weighted lists, but instead found {type(value)}")
        return tuple(value) if isinstance(value, range) else value

    def resolve_plando_form(self, value: str | list | dict) -> str:
        while True:
            if isinstance(value, list):
                value = random.choice(value)
            elif isinstance(value, dict):
                for v in value.values():
                    if not isinstance(v, int):
                        raise OptionError(f"Option {self.__class__.__name__} contains a list with a non-integer "
                                          f"weight {v} ({type(v)})")
                value = random.choices(tuple(value), tuple(value.values()))
            elif isinstance(value, str):
                if "," in value:
                    value = value.split(",")
                elif value in unique_forms:
                    break
                else:
                    raise OptionError(f"Option {self.__class__.__name__} contains invalid string value {value}")
            else:
                raise OptionError(f"Option {self.__class__.__name__} as a list expects strings, nested lists, "
                                  f"and nested weighted lists, but instead found {type(value)}")
        return value


class Dexsanity(Range, DexsanityResolver):
    """
    Adds a number of locations that can be checked by catching a certain pokemon species
    and registering it in the pokedex. The actual maximum number of added checks depends
    on what pokemon species are actually obtainable in the wild.

    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.

    Alternatively, you can put in a list of dex numbers, names, ranges, lists, and
    weighted lists in order to plando what pokemon you want to have locations for:
    ```
    dexsanity:
    - [50, 51, Maractus, 460-469, [1, 4, 7, Wurmple], {150: 5, 151: 1, Abra: 1}, 500]

    ```
    See the options guides for more information.
    """
    display_name = "Dexsanity"
    value: int | list[int]
    default = 0
    range_start = 0
    range_end = 649

    def __init__(self, value: Any):
        if isinstance(value, Iterable):  # Strings should be caught in from_any
            self.value = sorted(set(vv for v in value for vv in self.resolve_plando_dex(v)))  # Get rid of duplicates and stay deterministic
        else:
            super().__init__(value)

    @classmethod
    def from_any(cls, data: Any) -> Self:
        if isinstance(data, str):
            return cls.from_text(str(data))
        if isinstance(data, (Iterable, int)):
            return cls(data)
        raise OptionError(f"Unsupported type for {cls.__name__}: {type(data)}")


class Trainersanity(Range):
    """
    Adds a number of locations that can be checked by defeating a regular trainer.
    """
    display_name = "Trainersanity"
    default = 0
    range_start = 0
    range_end = 1


class Dexcountsanity(ExtendedOptionCounter):
    """
    Adds a number of locations that can be checked by catching a certain total number of
    species. This option consists of more than just one value:

    - **Maximum** (0-649) - The highest number of pokemon that will have a check.
    - **Steps** (1-649) - Excludes all locations with a count that is not dividable by
        this value, except **Maximum** (but only if there are actually **<Maximum>**
        pokemon species catchable).
    - **Leniency** (0-648) - Makes all checks logically require this many more pokemon
        species being available.

    Every parameter can be specified as unweighted/weighted lists, "random",
    and "random-range-x-y" like usual range options.

    The actual maximum number of added checks depends on how many different
    species are actually obtainable in the wild.
    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.
    """
    display_name = "Dexcountsanity"
    fill_defaults = True
    valid_keys = [
        "Maximum",
        "Steps",
        "Leniency",
    ]
    default = {
        "Maximum": 0,
        "Steps": 1,
        "Leniency": 0,
    }
    individual_min_max = {
        "Maximum": (0, 649),
        "Steps": (1, 649),
        "Leniency": (0, 648),
    }


class Seensanity(Range, DexsanityResolver):
    """
    Adds a number of locations that can be checked by seeing a certain Pokemon species,
    which is marked in the pokedex. The actual maximum number of added checks depends on
    what pokemon species are actually observable in the wild or in trainer battles.

    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.

    Alternatively, you can plando your Seensanity checks the same way as in Dexsanity.
    See the options guides for more information.
    """
    display_name = "Seensanity"
    value: int | list[int]
    default = 0
    range_start = 0
    range_end = 649

    def __init__(self, value: Any):
        if isinstance(value, Iterable):  # Strings should be caught in from_any
            self.value = sorted(set(vv for v in value for vv in self.resolve_plando_dex(v)))  # Get rid of duplicates and stay deterministic
        else:
            super().__init__(value)

    @classmethod
    def from_any(cls, data: Any) -> Self:
        if isinstance(data, str):
            return cls.from_text(str(data))
        if isinstance(data, (Iterable, int)):
            return cls(data)
        raise OptionError(f"Unsupported type for {cls.__name__}: {type(data)}")


class Seencountsanity(ExtendedOptionCounter):
    """
    A combination of Dexcountsanity and Seensanity.
    This option can be edited like Dexcountsanity, while only requiring to see a certain
    amount of Pokemon species.

    This option requires installing the Dexsanitysanity plugin. Otherwise, it will be ignored.
    """
    display_name = "Seencountsanity"
    fill_defaults = True
    visibility = DEXSANITYSANITY_VISIBILITY
    valid_keys = [
        "Maximum",
        "Steps",
        "Leniency",
    ]
    default = {
        "Maximum": 0,
        "Steps": 1,
        "Leniency": 0,
    }
    individual_min_max = {
        "Maximum": (0, 649),
        "Steps": (1, 649),
        "Leniency": (0, 648),
    }

    @classmethod
    def from_any(cls, data: Dict[str, Any]):
        return super().from_any(data if DEXSANITYSANITY_ENABLED else cls.default)


class Formsanity(Range, DexsanityResolver):
    """
    Adds a number of locations that can be checked by seeing a specific form of certain
    pokemon species. The actual maximum number of added checks depends on what pokemon
    species are actually obtainable in the wild and in trainer battles.

    If you want to have all 72 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.

    Alternatively, you can put in a list of form names and (weighted or unweighted)
    form name lists in order to plando what forms you want to have locations for:
    ```
    formsanity:
    - ["Unown (M)", ["Unown (B)", "Darmanitan (Zen)"], {"Meloetta (Aria)": 5, "Unown (W)": 1}]

    ```
    See the options guides for more information.
    """
    display_name = "Formsanity"
    value: int | list[str]
    default = 0
    range_start = 0
    range_end = 72

    def __init__(self, value: Any):
        if isinstance(value, Iterable):
            self.value = sorted(set(vv for v in value for vv in self.resolve_plando_form(v)))  # Get rid of duplicates and stay deterministic
        else:
            super().__init__(value)

    @classmethod
    def from_any(cls, data: Any) -> Range:
        if type(data) is int or isinstance(data, Iterable):
            return cls(data)
        return cls.from_text(str(data))


class Formcountsanity(ExtendedOptionCounter):
    """
    A combination of Dexcountsanity and Formsanity.
    This option can be edited like Dexcountsanity, while only requiring to see a certain
    amount of unique forms.

    This option requires installing the Dexsanitysanity plugin. Otherwise, it will be ignored.
    """
    display_name = "Formcountsanity"
    fill_defaults = True
    visibility = DEXSANITYSANITY_VISIBILITY
    valid_keys = [
        "Maximum",
        "Steps",
        "Leniency",
    ]
    default = {
        "Maximum": 0,
        "Steps": 1,
        "Leniency": 0,
    }
    individual_min_max = {
        "Maximum": (0, 72),
        "Steps": (1, 72),
        "Leniency": (0, 71),
    }

    @classmethod
    def from_any(cls, data: Dict[str, Any]):
        return super().from_any(data if DEXSANITYSANITY_ENABLED else cls.default)


class Shinysanity(Toggle, DexsanityResolver):
    """
    Adds a location for a randomly picked pokemon species to be seen in its shiny form.

    By editing your yaml with a text editor, you can set this option to any value in
    range 0-649 in order to have more than just one location. Otherwise, this option will
    be shown as a simple toggle. This also supports random-range-x-y.
    Adding at least one location enables an ingame option in the PC to change the shiny
    rate up to (almost) guaranteed.
    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.

    Alternatively, you can plando your Shinysanity checks the same way as in Dexsanity.
    See the options guides for more information.
    """
    display_name = "Shinysanity"
    value: int | list[int]
    default = 0

    def __init__(self, value: Any):
        if isinstance(value, Iterable):  # Strings should be caught in from_any
            self.value = sorted(set(vv for v in value for vv in self.resolve_plando_dex(v)))  # Get rid of duplicates and stay deterministic
        elif isinstance(value, int):
            if not 0 <= value <= 649:
                raise OptionError(f"Option {self.__class__.__name__}'s value {value} is not in range 0-649")
            self.value = value
        else:
            super().__init__(value)

    @classmethod
    def from_text(cls, text: str) -> Self:
        if text.startswith("random-range-"):
            parts = text.split("-")
            if len(parts) != 4 or not parts[2].isnumeric() or not parts[3].isnumeric():
                raise OptionError(f"Option {cls.__name__} does not support a value of {text}")
            range_min, range_max = int(parts[2]), int(parts[3])
            if range_max > 649 or range_min < 0:
                raise OptionError(f"Option {cls.__name__}'s random range {text} is out of bounds")
            return cls(random.randint(range_min, range_max))
        return super().from_text(text)

    @classmethod
    def get_option_name(cls, value):
        return ["No", "Yes"][int(value)] if value in (0, 1) else str(value)

    @classmethod
    def from_any(cls, data: Any) -> Self:
        if isinstance(data, str):
            return cls.from_text(str(data))
        if isinstance(data, (Iterable, int)):
            return cls(data)
        raise OptionError(f"Unsupported type for {cls.__name__}: {type(data)}")


class Shinycountsanity(Toggle, ExtendedOptionCounter):
    """
    A combination of **Shinysanity** and **Dexcountsanity**.
    This can, like with **Shinysanity**, be edited in a text editor to
    work like the regular **Dexcountsanity** option. Otherwise, it will
    be shown as a toggle. However, using this like **Dexcountsanity**
    requires you to put the key-value pairs as a list entry, i.e.:
    ```
    shinycountsanity:
    - Maximum: 10
      Steps: 2
      Leniency: 5

    ```

    This option requires installing the Dexsanitysanity plugin.
    Otherwise, it will be ignored.
    """
    display_name = "Shinycountsanity"
    value: int | dict[str, int]
    default = 0
    fill_defaults = True
    supports_weighting = True
    visibility = DEXSANITYSANITY_VISIBILITY
    individual_min_max = {
        "Maximum": (0, 649),
        "Steps": (1, 649),
        "Leniency": (0, 648),
    }

    def __init__(self, value: int | dict[str, int]) -> None:
        if isinstance(value, dict):
            self.value = {key: val for key, val in value.items()}
        elif isinstance(value, int):
            self.value = {
                "Maximum": value,
                "Steps": 1,
                "Leniency": 0,
            }
        else:
            raise OptionError(f"Option {self.__class__.__name__} does not support a value of type {type(value)}")

    @classmethod
    def from_any(cls, data: Any) -> Self:
        default = {
            "Maximum": 0,
            "Steps": 1,
            "Leniency": 0,
        }
        valid_keys = [
            "Maximum",
            "Steps",
            "Leniency",
        ]
        if not DEXSANITYSANITY_ENABLED:
            return cls(cls.default)
        if type(data) is str:
            return cls.from_text(data)
        if isinstance(data, int):
            return cls(data)
        if not isinstance(data, dict):
            raise OptionError(f"Option {cls.__name__} does not support a value of type {type(data)}")
        data = data.copy()
        if cls.fill_defaults:
            for key in valid_keys:
                if key not in data:
                    if key in default:
                        data[key] = default[key]
                    else:
                        data[key] = 0
                data[key] = cls.resolve_value(data[key], key)
        return cls(data)

    @classmethod
    def get_option_name(cls, value):
        return ["No", "Yes"][int(value)] if value in (0, 1) else str(value)


class Shinyformsanity(Toggle, DexsanityResolver):
    """
    A combination for **Shinysanity** and **Formsanity**.
    It works pretty much like **Shinysanity**, including being shown as a simple toggle
    outside the template yaml, while only requiring to see the shiny version of specific
    forms. It also contains plando capabilities in the way that **Formsanity** has them.

    This option requires installing the Dexsanitysanity plugin. Otherwise, it will be ignored.
    """
    display_name = "Shinyformsanity"
    value: int | list[str]
    visibility = DEXSANITYSANITY_VISIBILITY
    default = 0

    def __init__(self, value: Any):
        if isinstance(value, Iterable):
            self.value = sorted(set(vv for v in value for vv in self.resolve_plando_form(v)))  # Get rid of duplicates and stay deterministic
        else:
            super().__init__(value)

    @classmethod
    def from_text(cls, text: str) -> Toggle:
        if text.startswith("random-range-"):
            parts = text.split("-")
            if len(parts) != 4 or not parts[2].isnumeric() or not parts[3].isnumeric():
                raise OptionError(f"Option {cls.__name__} does not support a value of {text}")
            range_min, range_max = int(parts[2]), int(parts[3])
            if range_max > 649 or range_min < 0:
                raise OptionError(f"Option {cls.__name__}'s random range {text} is out of bounds")
            return cls(random.randint(range_min, range_max))
        return super().from_text(text)

    @classmethod
    def from_any(cls, data: Any) -> Self:
        if not DEXSANITYSANITY_ENABLED:
            return cls(cls.default)
        if type(data) is str:
            return cls.from_text(data)
        if isinstance(data, (Iterable, int)):
            return cls(data)
        raise OptionError(f"Unsupported type for {cls.__name__}: {type(data)}")

    @classmethod
    def get_option_name(cls, value):
        return ["No", "Yes"][int(value)] if value in (0, 1) else str(value)


class Shinyformcountsanity(Toggle, ExtendedOptionCounter):
    """
    A combination of **Shinysanity**, **Formsanity**, and **Dexcountsanity**.
    It works pretty much like **Shinycountsanity**, including being shown as a simple
    toggle outside the template yaml, while only requiring to see a certain amount of
    unique forms in their shiny variant.

    This option requires installing the Dexsanitysanity plugin. Otherwise, it will be ignored.
    """
    display_name = "Shinyformcountsanity"
    value: dict[str, int]
    default = 0
    fill_defaults = True
    supports_weighting = True
    visibility = DEXSANITYSANITY_VISIBILITY
    individual_min_max = {
        "Maximum": (0, 72),
        "Steps": (1, 72),
        "Leniency": (0, 71),
    }

    def __init__(self, value: int | dict[str, int]) -> None:
        if isinstance(value, dict):
            self.value = {key: val for key, val in value.items()}
        elif isinstance(value, int):
            self.value = {
                "Maximum": value,
                "Steps": 1,
                "Leniency": 0,
            }
        else:
            raise OptionError(f"Option {self.__class__.__name__} does not support a value of type {type(value)}")

    @classmethod
    def from_any(cls, data: Any) -> Self:
        default = {
            "Maximum": 0,
            "Steps": 1,
            "Leniency": 0,
        }
        valid_keys = [
            "Maximum",
            "Steps",
            "Leniency",
        ]
        if not DEXSANITYSANITY_ENABLED:
            return cls(cls.default)
        if type(data) is str:
            return cls.from_text(data)
        elif isinstance(data, int):
            return cls(data)
        if not isinstance(data, dict):
            raise OptionError(f"Option {cls.__name__} does not support a value of type {type(data)}")
        data = data.copy()
        if cls.fill_defaults:
            for key in valid_keys:
                if key not in data:
                    if key in default:
                        data[key] = default[key]
                    else:
                        data[key] = 0
                data[key] = cls.resolve_value(data[key], key)
        return cls(data)

    @classmethod
    def get_option_name(cls, value):
        return ["No", "Yes"][int(value)] if value in (0, 1) else str(value)


# Gendersanity

# Gendercountsanity
# Shinygendersanity

# Shinygendercountsanity
