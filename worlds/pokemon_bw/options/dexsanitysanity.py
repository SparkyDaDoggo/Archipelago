from typing import Any, Iterable

from Options import Range
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
                    raise Exception(f"Option {self.__class__.__name__} as a list expects integers, found {type(val)}")
                if val < 1:
                    raise Exception(f"Option {self.__class__.__name__} contains dex number {val}, "
                                    f"which is lower than minimum 1")
                elif val > self.range_end:
                    raise Exception(f"Option {self.__class__.__name__} contains dex number {val}, "
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

    - **Maximum** - The highest number of pokemon that will have a check.
    - **Steps** - Excludes all locations with a count that is not dividable by this
        value, except **Maximum** (but only if there are actually **<Maximum>** pokemon
        species catchable).
    - **Leniency** - Makes all checks logically require this many more pokemon species
        being available.

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


# Formsanity
# Shinysanity
# Gendersanity

# Seencountsanity
# Formcountsanity
# Gendercountsanity
# Shinyformsanity
# Shinygendersanity
# Shinycountsanity

# Shinyformcountsanity
# Shinygendercountsanity
