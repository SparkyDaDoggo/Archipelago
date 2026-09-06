import random
from typing import Any, Iterable, Self, Dict

from Options import Range, Toggle, OptionError, Visibility
from ..data.common_options import ExtendedOptionCounter
from worlds import world_sources

DEXSANITYSANITY_ENABLED = any(source.name == "pokemon_bw_dexsanitysanity" for source in world_sources)


class Dexsanity(Range):
    """
    Adds a number of locations that can be checked by catching a certain pokemon species
    and registering it in the pokedex. The actual maximum number of added checks depends
    on what pokemon species are actually obtainable in the wild.

    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.

    Alternatively, you can put in a list of dex numbers and dex number ranges in order to
    plando what pokemon you want to have locations for:
    ```
      dexsanity:
        - [50, 51, 52, 53, 54, 460-469, 500]
    ```
    See the options guides for more information.
    """
    display_name = "Dexsanity"
    value: int | list[int]
    default = 0
    range_start = 0
    range_end = 649

    def __init__(self, value: Any):
        if isinstance(value, Iterable):
            resolved = []
            for val in value:
                if isinstance(val, str):
                    split = val.split("-")
                    if len(split) != 2 or not split[0].isnumeric() or not split[1].isnumeric():
                        raise OptionError(f"Option {self.__class__.__name__} contains invalid range {val}")
                    rang = int(split[0]), int(split[1])
                    if not (1 < rang[0] <= self.range_end) or not (1 < rang[1] <= self.range_end):
                        raise OptionError(f"Option {self.__class__.__name__} contains invalid range {val}")
                    resolved.extend(range(rang[0], rang[1]+1))
                elif isinstance(val, int):
                    if val < 1:
                        raise OptionError(f"Option {self.__class__.__name__} contains dex number {val}, "
                                          f"which is lower than minimum 1")
                    elif val > self.range_end:
                        raise OptionError(f"Option {self.__class__.__name__} contains dex number {val}, "
                                          f"which is higher than maximum {self.range_end}")
                    resolved.append(val)
                else:
                    raise OptionError(f"Option {self.__class__.__name__} as a list expects integers and integer "
                                      f"ranges, found {type(val)}")
            self.value = sorted(set(resolved))  # Get rid of duplicates and stay deterministic
        else:
            super().__init__(value)

    @classmethod
    def from_any(cls, data: Any) -> Range:
        if type(data) is int or isinstance(data, Iterable):
            return cls(data)
        return cls.from_text(str(data))


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


class Seensanity(Range):
    """
    Adds a number of locations that can be checked by seeing a certain Pokemon species,
    which is marked in the pokedex. The actual maximum number of added checks depends on
    what pokemon species are actually observable in the wild or in trainer battles.

    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.

    Alternatively, you can put in a list of dex numbers and dex number ranges in order to
    plando what pokemon you want to have locations for:
    ```
      seensanity:
        - [50, 51, 52, 53, 54, 460-469, 500]
    ```
    See the options guides for more information.
    """
    display_name = "Seensanity"
    value: int | list[int]
    default = 0
    range_start = 0
    range_end = 649

    def __init__(self, value: Any):
        if isinstance(value, Iterable):
            resolved = []
            for val in value:
                if isinstance(val, str):
                    split = val.split("-")
                    if len(split) != 2 or not split[0].isnumeric() or not split[1].isnumeric():
                        raise OptionError(f"Option {self.__class__.__name__} contains invalid range {val}")
                    rang = int(split[0]), int(split[1])
                    if not (1 < rang[0] <= self.range_end) or not (1 < rang[1] <= self.range_end):
                        raise OptionError(f"Option {self.__class__.__name__} contains invalid range {val}")
                    resolved.extend(range(rang[0], rang[1]+1))
                elif isinstance(val, int):
                    if val < 1:
                        raise OptionError(f"Option {self.__class__.__name__} contains dex number {val}, "
                                          f"which is lower than minimum 1")
                    elif val > self.range_end:
                        raise OptionError(f"Option {self.__class__.__name__} contains dex number {val}, "
                                          f"which is higher than maximum {self.range_end}")
                    resolved.append(val)
                else:
                    raise OptionError(f"Option {self.__class__.__name__} as a list expects integers and integer "
                                      f"ranges, found {type(val)}")
            self.value = sorted(set(resolved))  # Get rid of duplicates and stay deterministic
        else:
            super().__init__(value)

    @classmethod
    def from_any(cls, data: Any) -> Range:
        if type(data) is int or isinstance(data, Iterable):
            return cls(data)
        return cls.from_text(str(data))


class Seencountsanity(ExtendedOptionCounter):
    """
    A combination of Dexcountsanity and Seensanity.
    This option can be edited like Dexcountsanity, while only requiring to see a certain
    amount of Pokemon species.
    """
    display_name = "Seencountsanity"
    fill_defaults = True
    visibility = Visibility.spoiler | Visibility.complex_ui
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


class Formsanity(Range):
    """
    Adds a number of locations that can be checked by seeing a specific form of certain
    pokemon species. The actual maximum number of added checks depends on what pokemon
    species are actually obtainable in the wild.

    If you want to have all 72 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.

    Alternatively, you can put in a list of form names in order to plando what forms you
    want to have locations for:
    ```
      formsanity:
      - ["Unown (M)", "Darmanitan (Zen)"]
    ```
    See the options guides for more information.
    """
    display_name = "Formsanity"
    value: int | list[str]
    default = 0
    range_start = 0
    range_end = 72

    def __init__(self, value: Any):
        from ..data.pokemon.species import unique_forms

        if isinstance(value, Iterable):
            resolved = []
            for val in value:
                if isinstance(val, str):
                    if val not in unique_forms:
                        raise OptionError(f"Option {self.__class__.__name__} contains form name {val}, "
                                          f"which is not an existing form")
                    resolved.append(val)
                else:
                    raise OptionError(f"Option {self.__class__.__name__} as a list expects strings, found {type(val)}")
            self.value = sorted(set(resolved))  # Get rid of duplicates and stay deterministic
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
    """
    display_name = "Formcountsanity"
    fill_defaults = True
    visibility = Visibility.spoiler | Visibility.complex_ui
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


class Shinysanity(Toggle):
    """
    Adds a location for a randomly picked pokemon species to be seen in its shiny form.

    By editing your yaml with a text editor, you can set this option to any value in
    range 0-649 in order to have more than just one location. Otherwise, this option will
    be shown as a simple toggle. This also supports random-range-x-y.
    Adding at least one location enables an ingame option in the PC to change the shiny
    rate up to (almost) guaranteed.
    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.

    Alternatively, you can put in a list of dex numbers in order to plando what pokemon
    you want to have locations for:
    ```
      shinysanity:
        - [50, 51, 52, 53, 54, 460, 461, 500]
    ```
    See the options guides for more information.
    """
    display_name = "Shinysanity"
    value: int | list[int]
    default = 0

    def __init__(self, value: Any):
        if isinstance(value, Iterable):
            resolved = []
            for val in value:
                if isinstance(val, str):
                    split = val.split("-")
                    if len(split) != 2 or not split[0].isnumeric() or not split[1].isnumeric():
                        raise OptionError(f"Option {self.__class__.__name__} contains invalid range {val}")
                    rang = int(split[0]), int(split[1])
                    if not (1 < rang[0] <= 649) or not (1 < rang[1] <= 649):
                        raise OptionError(f"Option {self.__class__.__name__} contains invalid range {val}")
                    resolved.extend(range(rang[0], rang[1]+1))
                elif isinstance(val, int):
                    if val < 1:
                        raise OptionError(f"Option {self.__class__.__name__} contains dex number {val}, "
                                          f"which is lower than minimum 1")
                    elif val > 649:
                        raise OptionError(f"Option {self.__class__.__name__} contains dex number {val}, "
                                          f"which is higher than maximum 649")
                    resolved.append(val)
                else:
                    raise OptionError(f"Option {self.__class__.__name__} as a list expects integers and integer "
                                      f"ranges, found {type(val)}")
            self.value = sorted(set(resolved))  # Get rid of duplicates and stay deterministic
        elif isinstance(value, int):
            if not 0 <= value <= 649:
                raise OptionError(f"Option {self.__class__.__name__}'s value {value} is not in range 0-649")
            self.value = value
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
        if type(data) is str:
            return cls.from_text(data)
        else:
            return cls(data)

    @classmethod
    def get_option_name(cls, value):
        return ["No", "Yes"][int(value)] if value in (0, 1) else str(value)


class Shinycountsanity(Toggle, ExtendedOptionCounter):
    """
    A combination of **Shinysanity** and **Dexcountsanity**.
    This can, like with **Shinysanity**, be edited in a text editor to work like the
    regular **Dexcountsanity** option. Otherwise, it will be shown as a toggle.
    However, using this like **Dexcountsanity** requires you to put the key-value pairs
    as a list entry, i.e.:
    ```
    shinycountsanity:
    - Maximum: 10
      Steps: 2
      Leniency: 5
    ```
    """
    display_name = "Shinycountsanity"
    value: int | dict[str, int]
    default = 0
    fill_defaults = True
    supports_weighting = True
    visibility = Visibility.spoiler | Visibility.complex_ui
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


class Shinyformsanity(Toggle):
    """
    A combination for **Shinysanity** and **Formsanity**.
    It works pretty much like **Shinysanity**, including being shown as a simple toggle
    outside the template yaml, while only requiring to see the shiny version of specific
    forms. It also contains plando capabilities in the way that **Formsanity** has them.
    """
    display_name = "Shinyformsanity"
    value: int | list[str]
    visibility = Visibility.spoiler | Visibility.complex_ui
    default = 0

    def __init__(self, value: Any):
        from ..data.pokemon.species import unique_forms

        if isinstance(value, Iterable):
            resolved = []
            for val in value:
                if isinstance(val, str):
                    if val not in unique_forms:
                        raise OptionError(f"Option {self.__class__.__name__} contains form name {val}, "
                                          f"which is not an existing form")
                    resolved.append(val)
                else:
                    raise OptionError(f"Option {self.__class__.__name__} as a list expects strings, found {type(val)}")
            self.value = sorted(set(resolved))  # Get rid of duplicates and stay deterministic
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
        return cls(data)

    @classmethod
    def get_option_name(cls, value):
        return ["No", "Yes"][int(value)] if value in (0, 1) else str(value)


class Shinyformcountsanity(Toggle, ExtendedOptionCounter):
    """
    A combination of **Shinysanity**, **Formsanity**, and **Dexcountsanity**.
    It works pretty much like **Shinycountsanity**, including being shown as a simple
    toggle outside the template yaml, while only requiring to see a certain amount of
    unique forms in their shiny variant.
    """
    display_name = "Shinyformcountsanity"
    value: dict[str, int]
    default = 0
    fill_defaults = True
    supports_weighting = True
    visibility = Visibility.spoiler | Visibility.complex_ui
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
