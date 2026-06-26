import logging
import typing
from copy import deepcopy
from dataclasses import dataclass

from BaseClasses import PlandoOptions
from Options import (Choice, PerGameCommonOptions, Range, Toggle, PlandoTexts, OptionError,
                     OptionCounter, StartInventoryPool, OptionDict, ItemSet)
from .encounter import (RandomizeWildPokemon, RandomizeGiftPokemon, RandomizeTradePokemon, RandomizeStarterPokemon,
                        RandomizeLegendaryPokemon, RandomizeStaticPokemon, RandomizeTrainerPokemon,
                        WildRandomizationBlacklist, TrainerRandomizationBlacklist, PokemonRandomizationAdjustments,
                        EncounterPlando)
from .stats import (RandomizeLevelUpMovesets, RandomizeEvolutions, RandomizeTypes, RandomizeAbilities,
                    RandomizeBaseStats, RandomizeCatchRates, RandomizeGenderRatio, RandomizeTMHMCompatibility,
                    StatsRandomizationAdjustments, StatsPlando)
from ..data.common_options import ToggleSet

if typing.TYPE_CHECKING:
    from worlds.AutoWorld import World


# Order of Option classes being rendered on the WebHost
# toggle
# textchoice
# choice
# namedrange
# range
# freetext
# optioncounter if valid keys or verify item name or verify location name
# optionlist if valid keys
# locationset if verify location names
# itemset if verify item names
# optionset if valid keys


class GameVersion(Choice):
    """
    Select your game version.
    """
    display_name = "Game Version"
    option_black = 0
    option_white = 1
    # option_dynamic = 2
    default = "random"


class Goal(Choice):
    """
    Determines what your goal is to consider the game beaten.

    - **Ghetsis** - Clear the main story by defeating Ghetsis
    - **Champion** - Become the champion by defeating Alder
    - **Cynthia** - Defeat Cynthia in Undella Town
    - **Cobalion** - Reach and defeat/catch Cobalion in Mistralton Cave
    - **TM/HM hunt** - Get all TMs and HMs and show them to a scientist at Castelia
        City's Central Plaza
    - **Seven Sages hunt** - Find the Seven Sages
    - **Legendary hunt** - Find and defeat/catch all (stationary available) legendary
        encounters, including Volcarona
    - **Pokemon master** - Complete the requirements of all other goals combined

    You can also combine multiple goals by providing a list of multiple option names:
    ```
    goal:
      - ["tmhm_hunt", "legendary_hunt"]
    ```
    See the options guides for more information.
    """
    # - **Regional pokedex** - Complete the Unova pokedex (requires wild Pokemon being randomized)
    # - **National pokedex** - Complete the national pokedex (requires wild Pokemon being randomized)
    # - **Custom pokedex** - Complete all dexsanity locations (requires wild Pokemon being randomized and dexsanity being set to at least 100)
    display_name = "Goal"
    option_ghetsis = 0
    option_champion = 1
    option_cynthia = 2
    option_cobalion = 3
    # option_regional_pokedex = 4
    # option_national_pokedex = 5
    # option_custom_pokedex = 6
    option_tmhm_hunt = 7
    option_seven_sages_hunt = 8
    option_legendary_hunt = 9
    option_pokemon_master = 10
    default = 0
    combined: list[str] | None = None

    @classmethod
    def from_any(cls, data: typing.Any):
        if isinstance(data, list):
            if not data:
                raise OptionError("Combined goals list must not be empty")
            if all((d in cls.options or d in cls.name_lookup) for d in data):
                c = cls(cls.option_pokemon_master)
                c.combined = [(d if isinstance(d, str) else cls.name_lookup[d]) for d in data]
                return c
            raise OptionError(f"Combined goals list has invalid entries: {data}")
        return super().from_any(data)


class ShuffleBadgeRewards(Choice):
    """
    Determines how gym badges are randomized and what items gym badge locations can have.

    - **Vanilla** - Gym badges will stay at their vanilla locations.
    - **Shuffle** - Gym badges are shuffled between the gym leaders.
    - **Anything** - Gym badges can be anywhere and gym leaders can give any item.
    """
    # - **Any badge** - Puts the badges into the item pool, while only allowing items that have the word "badge" in
    #     their name (which also applies to gym badges of other games/worlds) being placed at gym leaders.
    display_name = "Shuffle Badge Rewards"
    option_vanilla = 0
    option_shuffle = 1
    # option_any_badge = 2
    option_anything = 3
    default = 1

    @classmethod
    def from_any(cls, data: typing.Any):
        if data == 2:
            return super().from_any(1)
        if data == "any_badge":
            return super().from_any("shuffle")
        return super().from_any(data)


class ShuffleTMRewards(Choice):
    """
    Determines what items NPCs, who would normally give TMs or HMs, can have.

    - **Shuffle** - These NPCs will always give a TM or HM from the same world.
    - **HM with Badge** - Like "Shuffle", but puts each HM (and TM70 Flash) at a gym
        leader's badge reward (including the TM from Clay on route 6).
    - **Anything** - No restrictions.
    """
    # - **Any TM/HM** - These NPCs will give any item that starts with "TM" or "HM" followed by any digit
    #     (which also applies to TMs and HMs of other games/worlds).
    display_name = "Shuffle TM Rewards"
    option_shuffle = 0
    option_hm_with_badge = 1
    # option_any_tm_hm = 2
    option_anything = 3
    default = 0

    @classmethod
    def from_any(cls, data: typing.Any):
        if data == 2:
            return super().from_any(0)
        if data == "any_tm_hm":
            return super().from_any("shuffle")
        return super().from_any(data)


class ShuffleRoadblockReqs(Toggle):
    """
    Roadblocks always require a specific item to disappear in this randomizer.
    If set to true, roadblocks will require a random key item.
    """
    display_name = "Shuffle Roadblock Requirements"
    default = False


class AdditionalRoadblocks(Choice):
    """
    Adds a number of additional roadblocks like cut trees or NPCs blocking your way
    across the region.
    """
    display_name = "Additional Roadblocks"
    option_none = 0
    option_some = 1
    option_many = 2
    default = 0


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

    def __init__(self, value: typing.Any):
        if isinstance(value, typing.Iterable):
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
    def from_any(cls, data: typing.Any) -> Range:
        if type(data) is int or isinstance(data, typing.Iterable):
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


class DoorShuffle(ToggleSet):
    """
    Shuffles or randomizes door warps.
    You can add as many of the following modifiers as you want.

    - **Gates** - Shuffles city gate entrances, leading to the region having a different
        layout than normally.
    - **Buildings per map** - Shuffles the building entrances (not gates) within every
        city or route.
    - **Buildings anywhere** - Shuffles building entrances (not gates) all over Unova.
    - **Dungeons** - Shuffles the location of all dungeons with two entrances and all
        dungeons with only one entrance.
    - **Full** - Fully shuffle all door warps. Overrides all modifiers above.
    - **Decoupled** - Removes the requirement for all shuffled door warps leading to
        each other.
    """
    display_name = "Door Shuffle"
    valid_keys_casefold = True
    valid_keys = [
        "Gates",
        "Buildings per map",
        "Buildings anywhere",
        "Dungeons",
        "Full",
        "Decoupled",
    ]
    default = []


class SeasonControl(Choice):
    """
    Determines how seasons are handled by the game.

    - **Vanilla** - Seasons are not randomized and change based on real time. Locations
        that depend on the season will only contain filler items.
    - **Changeable** - The current season can be changed by an NPC next to the Pokemon
        Center in Nimbasa City.
    - **Randomized** - All seasons are unlockable by items that get shuffled into the
        item pool. They can as well be changed by an NPC in Nimbasa City, with one season
        being unlocked from the beginning.
    """
    display_name = "Season Control"
    option_vanilla = 0
    option_changeable = 1
    option_randomized = 2
    default = 0


class AdjustLevels(ToggleSet):
    """
    Adjusts the levels of wild and trainer pokemon in areas that are in AP earlier
    accessible than in vanilla to not be significantly higher than in surrounding areas
    (regardless of randomization).
    You can add as many of the following modifiers as you want.

    - **Wild** - Normalizes wild pokemon levels, including surfing and fishing encounters.
    - **Trainer** - Normalizes trainer pokemon levels, excluding Cynthia.
    """
    display_name = "Adjust levels"
    is_wild = True
    is_trainer = True


class ModifyLevels(OptionCounter):  # Not ExtendedOptionCounter because too much plando
    """
    Modifies the level of all wild and trainer pokemon. You can choose a certain mode for
    each type of encounter. This is applied AFTER **Adjust Levels**.

    The mode decides how to apply the value to every pokemon. You can write either the
    name of the mode or the corresponding number:
    - **Multiply** or **0** - Multiply each level with value being seen as a percentage,
        i.e. 100 means no modifying. Allowed values are in range 1 to 10000.
    - **Add** or **1** - Add the value directly to each level (with negative values being
        allowed), i.e. 0 means no modifying. Allowed values are in range -99 to 99.
    - **Power** or **2** - Raise each level to the power of the value (which is seen as a
        percentage), i.e. 100 means no modifying. Allowed values are in range 1 to 700.

    An alternative way with more capabilities is to write this as a list with multiple
    key names (similar to most plando options). Every entry must include the keys `type`,
    `mode`, and `value`. All entries are individual calculations that are applied one
    after another. Be aware of rounding errors.
    Here is an example of how an entry can look like:
    ```
    - type: Either "Trainer" or "Wild"
      mode: Any mode described above (can as well be either the name or the number)
      value: The value like described above
    ```
    """
    display_name = "Modify levels"
    valid_keys = [
        "Trainer value",
        "Wild value",
        "Trainer mode",
        "Wild mode",
    ]
    default = {
        "Trainer value": 100,
        "Wild value": 100,
        "Trainer mode": 0,
        "Wild mode": 0,
    }
    value: dict[str, int] | list[dict[str, int | str]]

    def __init__(self, data: typing.Any):
        if isinstance(data, dict):
            super().__init__(data)
        elif isinstance(data, list):
            self.value = deepcopy(data)
        else:
            raise NotImplementedError(f"Cannot convert from non-dictionary, got {type(data)}")

    def get_option_name(self, value):
        if isinstance(value, dict):
            return super().get_option_name(value)
        elif isinstance(value, list):
            return ", ".join(map(str, value))

    @classmethod
    def from_any(cls, data: typing.Any) -> OptionDict:
        aliases = {
            "Multiply": 0,
            "Add": 1,
            "Power": 2,
        }
        if isinstance(data, dict):
            data: dict
            for key in cls.valid_keys:
                if key not in data:
                    if key in cls.default:
                        data[key] = cls.default[key]
                    else:
                        data[key] = 0
            for encounter in ("Trainer", "Wild"):
                key = encounter + " mode"
                if data[key] in aliases:
                    data[key] = aliases[data[key]]
            return cls(data)
        elif isinstance(data, list):
            data: list
            list_defaults = {
                "type": "Trainer",
                "mode": 0,
                "value": 100,
            }
            for entry in data:
                if not isinstance(entry, dict):
                    raise NotImplementedError(f"Cannot convert list entry from non-dictionary, got {type(entry)}")
                entry: dict
                for key in list_defaults:
                    if key not in entry:
                        entry[key] = list_defaults[key]
                if entry["mode"] in aliases:
                    entry["mode"] = aliases[entry["mode"]]
            return cls(data)
        else:
            raise NotImplementedError(f"Cannot convert from non-dictionary, got {type(data)}")

    def verify(self, world: typing.Type["World"], player_name: str, plando_options: PlandoOptions) -> None:

        errors = []
        mode_min_max: dict[int, tuple[int, int]] = {
            0: (1, 10000),
            1: (-99, 99),
            2: (1, 700),
        }

        if isinstance(self.value, dict):
            for encounter in ("Trainer", "Wild"):
                mode = self.value[f'{encounter} mode']
                if mode not in mode_min_max:
                    errors.append(f"Bad {encounter} mode {mode}")
                _min, _max = mode_min_max[mode]
                if not _min <= self.value[f"{encounter} value"] <= _max:
                    errors.append(f"{encounter} value {self.value[f'{encounter} value']} "
                                  f"out of range {_min} to {_max} for mode {mode}")
        elif isinstance(self.value, list):
            for entry in self.value:
                entry: dict[str, int | str]
                mode = entry["mode"]
                if mode not in mode_min_max:
                    errors.append(f"Bad {entry['type']} mode {mode}")
                _min, _max = mode_min_max[mode]
                if not _min <= entry["value"] <= _max:
                    errors.append(f"{entry['type']} value {entry['value']} "
                                  f"out of range {_min} to {_max} for mode {mode}")
        else:
            raise NotImplementedError(f"Cannot convert from non-dictionary, got {type(self.value)}")

        if len(errors) != 0:
            errors = [f"For option {getattr(self, 'display_name', self)} of player {player_name}:"] + errors
            raise OptionError("\n".join(errors))

    @staticmethod
    def is_modified(mode: int, value: int) -> bool:
        match mode:
            case 0:
                return value != 100
            case 1:
                return value != 0
            case 2:
                return value != 100
            case _:
                raise Exception(f"Bad mode {mode} in Modify Levels option")

    def is_trainer_modified(self) -> bool:
        if isinstance(self.value, dict):
            return self.is_modified(self.value["Trainer mode"], self.value["Trainer value"])
        elif isinstance(self.value, list):
            for entry in self.value:
                if entry["type"] == "Trainer" and self.is_modified(entry["mode"], entry["value"]):
                    return True
            return False
        else:
            raise NotImplementedError(f"Cannot convert from non-dictionary, got {type(self.value)}")

    def is_wild_modified(self) -> bool:
        if isinstance(self.value, dict):
            return self.is_modified(self.value["Wild mode"], self.value["Wild value"])
        elif isinstance(self.value, list):
            for entry in self.value:
                if entry["type"] == "Wild" and self.is_modified(entry["mode"], entry["value"]):
                    return True
            return False
        else:
            raise NotImplementedError(f"Cannot convert from non-dictionary, got {type(self.value)}")

    def is_any_modified(self) -> bool:
        return self.is_wild_modified() or self.is_trainer_modified()

    @staticmethod
    def cap(level: int):
        return max(min(level, 100), 1)

    @classmethod
    def modify_trainer(cls, value: dict[str, int] | list[dict[str, int | str]], level) -> int:
        if isinstance(value, dict):
            return cls.modify(value["Trainer mode"], value["Trainer value"], level)
        elif isinstance(value, list):
            calc = level
            for entry in value:
                if entry["type"] == "Trainer":
                    calc = cls.modify(entry["mode"], entry["value"], calc)
            return calc
        else:
            raise NotImplementedError(f"Cannot convert from non-dictionary, got {type(value)}")

    @classmethod
    def modify_wild(cls, value: dict[str, int] | list[dict[str, int | str]], level) -> int:
        if isinstance(value, dict):
            return cls.modify(value["Wild mode"], value["Wild value"], level)
        elif isinstance(value, list):
            calc = level
            for entry in value:
                if entry["type"] == "Wild":
                    calc = cls.modify(entry["mode"], entry["value"], calc)
            return calc
        else:
            raise NotImplementedError(f"Cannot convert from non-dictionary, got {type(value)}")

    @classmethod
    def modify(cls, mode: int, value: int, level: int) -> int:
        match mode:
            case 0:
                return cls.cap((level * value) // 100)
            case 1:
                return cls.cap(level + value)
            case 2:
                return cls.cap(int(level ** (value / 100)))
            case _:
                raise Exception(f"Bad mode {mode} in Modify Levels option")


class ModifyEncounterRates(Choice):
    """
    Modifies the encounter slot rates for wild encounters.

    - **Vanilla** - Keeps the vanilla encounter slot rates.
    - **Try normalized** - Normalizes the rates for the 12 grass method slots to 8-9%
        each and the rates for surfing and fishing method slots to 20% each.
    - **Try normalized alternative** - Same as **Try normalized**, but sets 9 slots to
        10% each and 3 slots to 3-4% each for grass methods.
    - **Invasive** - Sets one slot to 65-80%, one slot to 10-15%, and the remaining slots
        to 5% or less each for all encounter methods.
    - **One per method** - Sets all slots (except one) to 1%. Best in combination with
        **Prevent rare encounters**.
    - **Dexsanity friendly** - Sets two slots to 33-34%, one slot to 24%, and the
        remaining slots to 1% for grass method. For surfing and fishing methods, all
        slots (except one) are set to 1%. Best in combination with **Prevent rare encounters**.
    - **Randomized (12)** - Distributes the encounter rates randomly between all 12 grass
        methods slots, 5 surfing methods slots, and 5 fishing methods slots. All slots
        will still have at least a 1% rate. Expect multiple 1% slot rates.

    Alternatively, you can provide a list of custom encounter rates. See the option
    guides for more information.
    """
    display_name = "Modify Encounter Rates"
    value: int | dict[str, list[int]]
    option_vanilla = 0
    option_try_normalized = 1
    option_try_normalized_alt = 2
    # option_force_normalized_10 = 3
    # option_force_normalized_5 = 4
    option_invasive = 10
    option_one_per_method = 11
    option_dexsanity_friendly = 12
    option_randomized_12 = 20
    # option_randomized_10 = 21
    default = 0

    def __init__(self, value: int | dict):
        super().__init__(value)
        self.custom_rates: tuple[list[int], ...] | None = None

    @classmethod
    def from_any(cls, data: typing.Any) -> Choice:
        if isinstance(data, dict):
            reasons: list[str] = []
            for key, value in data.items():
                if key.casefold() not in ("grass", "surfing", "fishing"):
                    reasons.append(f"Unsupported method '{key}'")
                if not isinstance(value, typing.Iterable) or any(not isinstance(val, int) for val in value):
                    reasons.append(f"Unsupported value for method '{key}'")
                value: list[int]
                if key.casefold() == "grass" and not (12 <= len(value) <= 12):  # TODO change to 6 <= ... when enabling less slots
                    reasons.append(f"Unsupported list length ({len(value)}) for method '{key}'")
                if key.casefold() != "grass" and len(value) != 5:
                    reasons.append(f"Unsupported list length ({len(value)}) for method '{key}'")
                if sum(value) != 100 or any(val <= 0 for val in value):
                    reasons.append(f"Unsupported list values ({value}) for method '{key}'")
            if reasons:
                raise OptionError("Bad plando formatting for modify_encounter_rates option:\n" + ", ".join(reasons))
            data: dict[str, list[int]]
            return cls({key.casefold(): [val for val in value] for key, value in data.items()})
        return super().from_any(data)

    def __eq__(self, other):
        if other == "plando":
            return isinstance(self.value, dict)
        else:
            return super().__eq__(other)

    @property
    def current_key(self) -> str:
        if isinstance(self.value, dict):
            return "plando"
        else:
            return self.name_lookup[self.value]

    @classmethod
    def get_option_name(cls, value: int | dict[str, list[int]]) -> str:
        if not isinstance(value, int):
            return str(value)
        else:
            return super().get_option_name(value)


class ExpMultiplier(Range):
    """
    Multiplies the experience points received from defeating wild and trainer pokemon.
    """
    display_name = "Experience Multiplier"
    default = 1
    range_start = 1
    range_end = 100


class AllPokemonSeen(Toggle):
    """
    Start with all pokemon seen in your Pokedex.
    This allows you to see where the pokemon can be encountered in the wild.
    """
    display_name = "All Pokemon Seen"
    default = False


class AddFairyType(Choice):
    """
    Adds the fairy type from the sixth generation games.

    - **No** - Don't add the fairy type.
    - **Only randomized** - If types are randomized, this adds the fairy type to the pool
        of possible types.
    - **Modify vanilla** - Updates the type combination of all pokemon that received the
        fairy type in X and Y.
    """
    display_name = "Add Fairy Type"
    option_no = 0
    option_only_randomized = 1
    option_modify_vanilla = 2
    default = 0


class ReplaceEvoMethods(ToggleSet):
    """
    Replaces certain vanilla evolution methods with other methods that are easier to
    achieve. This also excludes them from randomized evolutions. Trade and time based
    evolutions are always replaced/excluded.
    You can add as many of the following modifiers as you want.

    - **Locations** - Replaces evolutions requiring a magnetic place, the mossy rock, or
        the ice rock with using a thunder stone, leaf stone, and shiny stone (respectively).
    - **Friendship** - Replaces friendship based evolutions with level up evolutions.
    - **PID** - Replaces personality value based evolutions. Gender dependant evolutions
        lose their gender dependency, Wurmple's random evolutions will require a
        Butterfree/Venomoth in your party, and Burmy will also evolve into Mothim while
        having a Venomoth in your party. Be aware that this can lead to affected pokemon
        changing their gender when evolved.
    - **Stats** - Replaces Tyrogue's stat based evolutions with level up while holding a
        protein, iron, or carbos.
    """
    display_name = "Replace Evolution Methods"
    is_locations = False
    is_friendship = False
    is_pid = False, "PID"
    is_stats = False


class MasterBallSeller(ToggleSet):
    """
    Adds the possibility to buy or obtain an unlimited amount of Master Balls.
    You can select multiple sellers.
    If multiple cost modifiers are added, a random cost in range between them (snapped to
    500-steps) gets selected. Adding no cost modifier defaults to 3000.

    - **Ns Castle** - Repurposes an NPC in N's Castle, who can be found in the same room
        as the grunt giving Ultra Balls to the player, to give/sell Master Balls to the player.
    - **PC** - Adds an option to every PC in Pokemon Centers to buy/obtain Master Balls.
    - **Cherens Mom** - Repurposes Cheren's Mom in Nuvema Town to give/sell Master Balls.
    - **Undella Mansion seller** - Adds the Master Ball to the pool of items that you can
        buy from the evolution items seller in the Undella Mansion for a random price.
        His offers are not affected by any cost modifier.
    - **Cost Free** - Makes Master Balls (potentially) cost nothing.
    - **Cost X** - Makes Master Balls (potentially) cost X Pokedollars. X can be any
        number in range of 0 to 30000.
    """
    display_name = "Master Ball Seller"
    is_ns_castle = False, "Ns Castle"
    is_pc = False, "PC"
    is_cherens_mom = False, "Cherens Mom"
    is_undella_mansion = False, "Undella Mansion seller"
    is_cost_free = False, "Cost Free"
    is_cost_1000 = False
    is_cost_3000 = False
    is_cost_10000 = False
    aliases_convert = [
        ("Cost: Free", "Cost Free"),
        ("Cost: 1000", "Cost 1000"),
        ("Cost: 3000", "Cost 3000"),
        ("Cost: 10000", "Cost 10000"),
        ("N's Castle", "Ns Castle"),
        ("Cheren's Mom", "Cherens Mom"),
    ]

    def verify_keys(self) -> None:
        dataset = set(word.casefold() for word in self.value)
        extra = dataset - set(key.casefold() for key in self._valid_keys)
        if extra:
            bad = []
            for key in extra:
                split = key.split()
                if (
                    len(split) != 2
                    or split[0] != "cost"
                    or not split[1].isnumeric()
                    or int(split[1]) not in range(0, 30001)
                ):
                    bad.append(key)
            if bad:
                raise OptionError(
                    f"Found unexpected key {', '.join(bad)} in {getattr(self, 'display_name', self)}. "
                    f"Allowed keys: {self._valid_keys} and \"Cost x\" for any x in range 0 to 30000."
                )


class WonderTrade(Toggle):
    """
    Enables pokemon being sent to and received from the datastorage wonder trade protocol.
    """
    display_name = "Wonder Trade"
    default = False


class MultiworldGiftPokemon(Toggle):
    """
    Adds pokemon to the item pool that can be obtained from an NPC in [TBD] after
    receiving the corresponding item from another player. Pokemon will only be placed in
    other worlds and have a species that matches the theme of that world (if defined).
    """
    display_name = "Multiworld Gift Pokemon"
    default = False


class TrapsProbability(Range):
    """
    Determines the probability of every randomly generated filler item being replaced by
    a random trap item.
    """
    display_name = "Traps Probability"
    default = 0
    range_start = 0
    range_end = 100


class ModifyItemPool(ToggleSet):
    """
    Modifies what items your world puts into the item pool.
    You can add as many of the following modifiers as you want.

    - **Useless key items** - Adds one of each unused key item with filler classification.
    - **Useful filler** - Main bag items that would normally occur only once can be
        generated multiple times.
    - **Ban bad filler** - Bans niche berries and mail from being generated as filler items.
    """
    display_name = "Modify Item Pool"
    is_useless_key_items = False
    is_useful_filler = False
    is_ban_bad_filler = False


class ModifyLogic(ToggleSet):
    """
    Modifies parts of what's logically required for various locations.
    You can add as many of the following modifiers as you want.

    - **Require Dowsing Machine** - Makes the Dowsing Machine a logical requirement to
        find hidden items.
    - **Require Flash** - Makes Mistralton Cave, Challenger's Cave, and the basement of
        Wellspring Cave logically require TM70 Flash.
    - **Consider <feature X>** - Toggles whether <feature X> is considered in logic to
        get access to some pokemon species. The available features are **evolutions**,
        **static pokemon**, **trades**, and **form change**. However, do note that trades
        are automatically excluded if evolutions are excluded and wild pokemon are not
        randomized.
    """
    # - **Prioritize key item locations** - Marks locations, that normally contain key items (which also includes
    #     badge rewards in gyms), as priority locations, making them mostly contain progressive items.
    display_name = "Modify Logic"
    is_require_dowsing = True, "Require Dowsing Machine"
    # is_prioritize_key_locs = True, "Prioritize key item locations"
    is_require_flash = True
    is_consider_evos = True, "Consider evolutions"
    is_consider_static = True, "Consider static pokemon"
    is_consider_trades = False
    is_consider_form_change = True
    ignore_deprecated = [
        "Prioritize key item locations",
    ]


class FillerItemsBlacklist(ItemSet):
    """
    Excludes these items from being thrown into the item pool as filler items.
    Items that are guaranteed to be in the item pool at least once, will stay.
    """
    display_name = "Filler Items Blacklist"


class FunnyDialog(Choice):
    """
    Adds humorous dialogue submitted by the folks in the Pokemon Black and White channel
    of the Archipelago Discord server. Alternatively, the efficient mode shortens many
    story lines for quicker playthroughs.

    This option requires Text Plando being enabled in the host settings.
    """
    display_name = "Funny Dialogue"
    option_none = 0
    option_funny = 1
    option_efficient = 2
    default = 0

    def verify(self, world: typing.Type["World"], player_name: str, plando_options: "PlandoOptions") -> None:
        from BaseClasses import PlandoOptions
        if self.current_key != "none" and not (PlandoOptions.texts & plando_options):
            # plando is disabled but plando options were given so overwrite the options
            self.value = []
            logging.warning(f"The plando texts module is turned off, "
                            f"so funny/efficient dialog for {player_name} will be ignored.")
        else:
            super().verify(world, player_name, plando_options)


class PokemonBWTextPlando(PlandoTexts):
    """
    Replaces specified text lines. Every entry follows the following format:
    ```
    - text: 'This is your text'
      at: text_key
      percentage: 100
    ```
    Refer to the Text Plando guide of this game for further information.
    """
    display_name = "Text Plando"
    default = [
        # ("story 160 0 7", "[c_100_#1_0] received [c_101_#1_1]![NextLine] Congratulations![Terminate]", 100),
        # ("system 172 0 1", "Huh? Why did you press the[NextLine]B button?[Terminate]", 100),
    ]

    def verify_keys(self) -> None:
        from ..patch.text import is_bad_text
        invalid = []
        for word in self:
            parts = word.at.casefold().split()
            reasons = []
            if len(parts) < 4:
                reasons.append("Not enough arguments: "+word.at)
            if len(parts) > 4:
                reasons.append("Too many arguments: "+word.at)
            if parts[0] not in ("system", "story"):
                reasons.append("Unknown module: "+parts[0])
            if not parts[1].isnumeric():
                reasons.append("File index is not a number: "+parts[1])
            if parts[0] == "system" and int(parts[1]) > 287:
                reasons.append(f"System file {parts[1]} does not exist")
            if parts[0] == "story" and int(parts[1]) > 471:
                reasons.append(f"Story file {parts[1]} does not exist")
            if not parts[2].isnumeric():
                reasons.append("Block index is not a number: "+parts[2])
            if not parts[3].isnumeric():
                reasons.append("Line index is not a number: "+parts[3])
            if word.text:
                bad = is_bad_text(word.text[0])
                if bad:
                    reasons.append("Bad text line: "+bad)
            if reasons:
                invalid.append((" ".join(parts), reasons))
        if invalid:
            raise OptionError(
                f"Invalid \"at\" placement{'s' if len(invalid) > 1 else ''} " +
                f"in {getattr(self, 'display_name', self)}:\n" +
                "\n".join((f"{entry[0]}: {', '.join(entry[1])}" for entry in invalid)) +
                "\nRefer to the Text Plando guide of this game for further information."
            )

    def to_slot_data(self) -> list[dict[str, str | list[str] | int]]:
        return [
            {
                "text": plando.text,
                "at": plando.at,
                "percentage": 100,  # Probabilities of all entries in self.value have already been rolled,
                                    # so passing the original percentage might discard even more
            }
            for plando in self
        ]


class PluginOptions(OptionDict):
    """This can be used to define certain options that are used by plugins.
    The main apworld will ignore this option entirely."""
    display_name = "Plugin Options"


class ReusableTMs(Choice):
    """
    Enables reusable TMs, allowing for the reuse of TMs.
    """
    display_name = "Reusable TMs"
    option_on = 0
    option_yes_please = 1
    option_of_course = 2
    option_im_not_a_masochist = 3
    default = 0
    _by_name = {"true": 0, "on": 0, "yes": 1, "yes_please": 1, "of_course": 2, "im_not_a_masochist": 3,
                "no": 4, "off_please": 5, "im_serious_no": 6, "im_a_masochist": 7}

    @classmethod
    def from_any(cls, data: typing.Any):
        if data == "yes":
            return super().from_any("yes_please")
        return super().from_any(data)

    @classmethod
    def from_text(cls, text: str) -> Choice:
        text = text.lower()
        no = ("no", "off_please", "im_serious_no", "im_a_masochist")
        if text in no:
            return cls(cls._by_name[text])
        return super().from_text(text)

    @property
    def current_key(self) -> str:
        no = {4: "no", 5: "off_please", 6: "im_serious_no", 7: "im_a_masochist"}
        if self.value in no:
            return no[self.value]
        return super().current_key


@dataclass
class PokemonBWOptions(PerGameCommonOptions):
    # General
    version: GameVersion
    goal: Goal

    # Pokemon encounters
    randomize_wild_pokemon: RandomizeWildPokemon
    randomize_trainer_pokemon: RandomizeTrainerPokemon
    # randomize_starter_pokemon: RandomizeStarterPokemon
    # randomize_static_pokemon: RandomizeStaticPokemon
    # randomize_gift_pokemon: RandomizeGiftPokemon
    # randomize_trade_pokemon: RandomizeTradePokemon
    # randomize_legendary_pokemon: RandomizeLegendaryPokemon
    pokemon_randomization_adjustments: PokemonRandomizationAdjustments
    encounter_plando: EncounterPlando
    wild_randomization_blacklist: WildRandomizationBlacklist
    trainer_randomization_blacklist: TrainerRandomizationBlacklist

    # Pokemon stats
    randomize_base_stats: RandomizeBaseStats
    randomize_evolutions: RandomizeEvolutions
    randomize_types: RandomizeTypes
    randomize_catch_rates: RandomizeCatchRates
    # randomize_gender_ratio: RandomizeGenderRatio
    randomize_level_up_movesets: RandomizeLevelUpMovesets
    # randomize_tm_hm_compatibility: RandomizeTMHMCompatibility
    # randomize_abilities: RandomizeAbilities
    # randomize_held_items: RandomizeHeldItems
    # randomize_egg_groups: RandomizeEggGroups
    stats_randomization_adjustments: StatsRandomizationAdjustments
    stats_plando: StatsPlando

    # Items, locations, and progression
    shuffle_badges: ShuffleBadgeRewards
    shuffle_tm_hm: ShuffleTMRewards
    # shuffle_roadblock_reqs: ShuffleRoadblockReqs
    # additional_roadblocks: AdditionalRoadblocks
    dexsanity: Dexsanity
    # trainersanity: Trainersanity
    # seensanity: Seensanity
    # formsanity: Formsanity
    # shinysanity: Shinysanity
    # door_shuffle: DoorShuffle
    season_control: SeasonControl
    modify_item_pool: ModifyItemPool
    modify_logic: ModifyLogic
    filler_items_blacklist: FillerItemsBlacklist

    # Miscellaneous
    adjust_levels: AdjustLevels
    modify_levels: ModifyLevels
    modify_encounter_rates: ModifyEncounterRates
    exp_multiplier: ExpMultiplier
    all_pokemon_seen: AllPokemonSeen
    # add_fairy_type: AddFairyType
    replace_evo_methods: ReplaceEvoMethods
    master_ball_seller: MasterBallSeller
    # deathlink: DeathLink  # Needs to be imported from base options
    # wonder_trade: WonderTrade
    # multiworld_gift_pokemon: MultiworldGiftPokemon
    # traps_probability: TrapsProbability
    start_inventory_from_pool: StartInventoryPool
    funny_dialog: FunnyDialog
    text_plando: PokemonBWTextPlando
    plugin_options: PluginOptions
    reusable_tms: ReusableTMs
