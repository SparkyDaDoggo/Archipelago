import random
from typing import Any, Iterable, Self

from Options import Range, Toggle, OptionError
from ..data.common_options import ExtendedOptionCounter


class Dexsanity(Range):
    """
    Adds a number of locations that can be checked by catching a certain pokemon species
    and registering it in the pokedex. The actual maximum number of added checks depends
    on what pokemon species are actually obtainable in the wild.

    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.

    Alternatively, you can put in a list of dex numbers in order to plando what pokemon
    you want to have locations for:
    ```
      dexsanity:
        - [50, 51, 52, 53, 54, 460, 461, 500]
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
            for val in value:
                if not type(val) is int:
                    raise OptionError(f"Option {self.__class__.__name__} as a list expects integers, found {type(val)}")
                if val < 1:
                    raise OptionError(f"Option {self.__class__.__name__} contains dex number {val}, "
                                      f"which is lower than minimum 1")
                elif val > self.range_end:
                    raise OptionError(f"Option {self.__class__.__name__} contains dex number {val}, "
                                      f"which is higher than maximum {self.range_end}")
            self.value = list(set(value))  # Get rid of duplicates
            self.value.sort()  # Very important to not make it non-deterministic
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


class Seensanity(Range):
    """
    Adds a number of locations that can be checked by seeing a certain Pokemon species,
    which is marked in the pokedex. The actual maximum number of added checks depends on
    what pokemon species are actually observable in the wild or in trainer battles.

    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.
    """
    display_name = "Seensanity"
    default = 0
    range_start = 0
    range_end = 649


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
            for val in value:
                if not type(val) is int:
                    raise OptionError(f"Option {self.__class__.__name__} as a list expects integers, found {type(val)}")
                if not 1 < val <= 649:
                    raise OptionError(f"Option {self.__class__.__name__} contains dex number {val}, "
                                      f"which is not in range 1-649")
            self.value = sorted(set(value))  # Get rid of duplicates and stay deterministic
        elif isinstance(value, int):
            if not 1 < value <= 649:
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
    """
    display_name = "Shinycountsanity"
    value: int | dict[str, int]
    default = 0
    fill_defaults = True
    individual_min_max = {
        "Maximum": (0, 649),
        "Steps": (1, 649),
        "Leniency": (0, 648),
    }

    def __init__(self, value: int | dict[str, int]) -> None:
        if isinstance(value, dict):
            super(ExtendedOptionCounter, self.__class__).__init__(value)
        elif isinstance(value, int):
            super().__init__(value)
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
        if type(data) is str:
            return cls.from_text(data)
        elif isinstance(data, int):
            return cls(data)
        elif isinstance(data, dict):
            data = data.copy()
            if cls.fill_defaults:
                for key in valid_keys:
                    if key not in data:
                        if key in default:
                            data[key] = default[key]
                        else:
                            data[key] = 0
                    data[key] = cls.resolve_value(data[key], key)
            return super
        else:
            raise OptionError(f"Option {cls.__name__} does not support a value of type {type(data)}")

    @classmethod
    def get_option_name(cls, value):
        return ["No", "Yes"][int(value)] if value in (0, 1) else str(value)


# Formsanity
# Gendersanity

# Formcountsanity
# Gendercountsanity
# Shinyformsanity
# Shinygendersanity
# Shinycountsanity

# Shinyformcountsanity
# Shinygendercountsanity
