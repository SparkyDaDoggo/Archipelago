
import logging
import typing
from copy import deepcopy
from dataclasses import dataclass

import settings
from BaseClasses import PlandoOptions
from Options import (Choice, PerGameCommonOptions, OptionSet, Range, Toggle,
                     PlandoTexts, OptionError, Option, OptionCounter, OptionDict)

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


class CasefoldOptionSet(OptionSet):
    valid_keys_casefold = True

    def __init__(self, value: typing.Iterable[str]):
        self.value = set(val.casefold() for val in value)
        super(OptionSet, self).__init__()  # To make it not call super.__init__? Not sure

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
    individual_min_max: dict[str, tuple[int, int]] = {}

    @classmethod
    def from_any(cls, data: typing.Dict[str, typing.Any]):
        if not isinstance(data, dict):
            raise NotImplementedError(f"Cannot Convert from non-dictionary, got {type(data)}")
        for key in cls.valid_keys:
            if key not in data:
                if key in cls.default:
                    data[key] = cls.default[key]
                else:
                    data[key] = 0
        return cls(data)

    def verify(self, world: type["World"], player_name: str, plando_options: PlandoOptions) -> None:
        super().verify(world, player_name, plando_options)

        errors = []

        for key in self.value:
            if key in self.individual_min_max:
                _min, _max = self.individual_min_max[key]
                if not _min <= self.value[key] <= _max:
                    errors.append(f"{key}: {self.value[key]} not in range {_min} to {_max}")

        if len(errors) != 0:
            errors = [f"For option {getattr(self, 'display_name', self)} of player {player_name}:"] + errors
            raise OptionError("\n".join(errors))


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
    - **TM/HM hunt** - Get all TMs and HMs
    - **Seven Sages hunt** - Find the Seven Sages
    - **Legendary hunt** - Find and defeat/catch all (stationary available) legendary encounters, including Volcarona
    - **Pokemon master** - Complete the requirements of all other goals combined
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


class RandomizeWildPokemon(CasefoldOptionSet):
    """
    Randomizes wild pokemon encounters.

    - **Randomize** - Toggles wild pokemon being randomized. Automatically added if any other modifier is added.
    - **Ensure all obtainable** - Ensures that every pokemon species is obtainable by either catching or evolving. This is automatically checked if **National pokedex** is chosen as the goal.
    - **Similar base stats** - Tries to keep every randomized pokemon at a similar base stat total as the replaced encounter.
    - **Type themed areas** - Tries to make every pokemon in an area have a certain same type.
    - **Area 1-to-1** - Keeps the amount of different encounters and their encounter rate in every area.
    - **Merge phenomenons** - Makes rustling grass, rippling water spots, dust clouds, and flying shadows in the same area have only one encounter. Takes priority over **Area 1-to-1**.
    - **Prevent rare encounters** - Randomizes the encounter slots with the lowest chance in each area to the same pokemon. Takes priority over **Area 1-to-1**.

    It is **highly recommended** to include **Prevent rare encounters** if you want to randomize wild pokemon,
    else you might find yourself searching for two 1% encounters on every route.
    """
    display_name = "Randomize Wild Pokemon"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "Ensure all obtainable",
        "Similar base stats",
        "Type themed areas",
        "Area 1-to-1",
        "Merge phenomenons",
        "Prevent rare encounters",
    ]
    default = []

    @classmethod
    def from_any(cls, data: typing.Any):
        option = super().from_any(data)
        if len(option.value) > 0 and "Randomize" not in option.value:
            option.value.add("randomize")
        return option


class RandomizeTrainerPokemon(CasefoldOptionSet):
    """
    Randomizes trainer pokemon.
    - **Randomize** - Toggles trainer pokemon being randomized. Automatically added if any other modifier is added.
    - **Similar base stats** - Tries to keep the randomized pokemon at a similar base stat total as the replaced one.
    """
    # - **Type themed** - All pokemon of a trainer have to share at least one randomly chosen type.
    #                           Gym leaders will always have themed teams, regardless of this modifier.
    # - **Themed gym trainers** - All pokemon of gym trainers will share the type assigned to the gym leader.
    display_name = "Randomize Trainer Pokemon"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "Similar base stats",
        # "Type themed",
        # "Themed gym trainers",

        # Not sure whether I really want to implement these:
        # "Randomize abilities",
        # "Randomize natures",
        # "Randomize held items",
        # "Only already with held item",
        # "Allow no held item",
        # "Randomize unique moves",
    ]
    require_randomize = {
        "Similar base stats",
        # "Type themed",
        # "Themed gym trainers",
    }
    default = []

    @classmethod
    def from_any(cls, data: typing.Any):
        option = super().from_any(data)
        if len(option.value.intersection(cls.require_randomize)) > 0 and "Randomize" not in option.value:
            option.value.add("randomize")
        return option


class RandomizeStarterPokemon(CasefoldOptionSet):
    """
    Randomizes the starter pokemon you receive at the start of the game.
    - **Randomize** - Toggles starter pokemon being randomized. Automatically added if any other modifier is added.
    - **Any base** - Only use unevolved/baby pokemon.
    - **Base with 2 evolutions** - Only use unevolved/baby pokemon that can evolve twice. Overrides **Any base**.
    - **Only official starters** - Only use pokemon that have been a starter in any mainline game. Overrides **Any base** and **Base with 2 evolutions**.
    - **Type variety** - Every starter will have types that are different from the other two.
    """
    display_name = "Randomize Starter Pokemon"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "Any base",
        "Base with 2 evolutions",
        "Only official starters"
        "Type variety",
    ]
    default = []

    @classmethod
    def from_any(cls, data: typing.Any):
        option = super().from_any(data)
        if len(option.value) > 0 and "Randomize" not in option.value:
            option.value.add("randomize")
        return option


class RandomizeStaticPokemon(CasefoldOptionSet):
    """
    Randomizes static encounters you can battle and catch throughout the game, e.g. Volcarona in Relic Castle.
    - **Randomize** - Toggles static pokemon being randomized. Automatically added if any other modifier is added.
    - **Similar base stats** - Tries to keep the randomized pokemon at a similar base stat total as the replaced one.
    - **Only base** - Only use unevolved Pokemon.
    - **No legendaries** - Exclude legendaries from being placed into static encounters.
    """
    display_name = "Randomize Static Pokemon"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "Similar base stats",
        "Only base",
        "No legendaries",
    ]
    default = []

    @classmethod
    def from_any(cls, data: typing.Any):
        option = super().from_any(data)
        if len(option.value) > 0 and "Randomize" not in option.value:
            option.value.add("randomize")
        return option


class RandomizeGiftPokemon(CasefoldOptionSet):
    """
    Randomizes gift pokemon that you receive for free, e.g. the Larvesta egg on route 18.
    - **Randomize** - Toggles gift pokemon being randomized. Automatically added if any other modifier is added.
    - **Similar base stats** - Tries to keep the randomized pokemon at a similar base stat total as the replaced one.
    - **No legendaries** - Exclude legendaries from being placed into gift encounters.
    """
    display_name = "Randomize Gift Pokemon"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "Similar base stats",
        "No legendaries",
    ]
    default = []

    @classmethod
    def from_any(cls, data: typing.Any):
        option = super().from_any(data)
        if len(option.value) > 0 and "Randomize" not in option.value:
            option.value.add("randomize")
        return option


class RandomizeTradePokemon(CasefoldOptionSet):
    """
    Randomizes trade offers from NPCs. Both **Randomize...** are automatically added if none of them but any other
    modifier is added.
    - **Randomize offer** - Toggles offered pokemon being randomized.
    - **Randomize request** - Toggles requested pokemon being randomized.
    - **Similar base stats** - Tries to keep the randomized pokemon at a similar base stat total as the replaced ones.
    - **Coupled base stats** - Tries to make offered and requested pokemon have similar base stats
    - **No legendaries** - Exclude legendaries from being placed into trades.
    """
    display_name = "Randomize Trade Pokemon"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize offer",
        "Randomize request",
        "Similar base stats",
        "Coupled base stats",
        "No legendaries",
    ]
    default = []

    @classmethod
    def from_any(cls, data: typing.Any):
        option = super().from_any(data)
        if len(option.value) > 0 and "Randomize offer" not in option.value and "Randomize request" not in option.value:
            option.value.add("randomize offer")
            option.value.add("randomize request")
        return option


class RandomizeLegendaryPokemon(CasefoldOptionSet):
    """
    Randomizes legendary and mythical encounters.
    - **Randomize** - Toggles legendary pokemon being randomized. Automatically added if any other modifier is added.
    - **Keep legendary** - Randomized pokemon will all still be legendaries or mythicals.
    - **No legendaries** - Exclude legendaries from being placed into these encounters.
    - **Similar base stats** - Tries to keep the randomized pokemon at a similar base stat total as the replaced one. Overrides **Keep legendary**.
    - **Same type** - Tries to keep at least one type of every encounter.

    Including **Keep legendary** AND **No legendaries** will instead only put pseudo legendaries into these encounters.
    """
    display_name = "Randomize Legendary Pokemon"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "Keep legendary",
        "No legendaries",
        "Similar base stats",
        "Same type",
    ]
    default = []

    @classmethod
    def from_any(cls, data: typing.Any):
        option = super().from_any(data)
        if len(option.value) > 0 and "Randomize" not in option.value:
            option.value.add("randomize")
        return option


class PokemonRandomizationAdjustments(ExtendedOptionCounter):
    """
    Adjust various parameters in various pokemon randomization options (more modifiers are planned).
    Any minimum parameter cannot be higher than its corresponding maximum parameter.
    - **Stats leniency** - The minimum difference between base stat totals of vanilla and randomized species (for options with **Similar base stats** activated). Allowed values are integers in range 0 to 1530.
    """
    display_name = "Pokemon Randomization Adjustments"
    valid_keys = [
        "Stats leniency",
    ]
    default = {
        "Stats leniency": 10,
    }
    individual_min_max = {
        "Stats leniency": (0, 1530),
    }


class PlandoEncounter(typing.NamedTuple):
    map: str
    seasons: list[str]
    method: str
    slots: list[int]
    species: list[str]


class EncounterPlando(Option[list[PlandoEncounter]]):
    """
    Places specific pokemon species at specific locations. Every entry follows the following format:
    ```
    - map: Name of map
      seasons: Season name(s), optional
      method: Grass/Dark grass/...
      slots: Slot number(s) (0-11), optional
      species: Name(s) of species, random if multiple
    ```
    Encounter Plando requires the corresponding host setting to be enabled, else it will be ignored for all players.
    Be aware that this can lead to generation failures when combined with other restrictive options.
    Refer to the Encounter Plando guide of this game for further information.
    """
    display_name = "Encounter Plando"
    supports_weighting = False
    default = []

    def __init__(self, value: typing.Iterable[PlandoEncounter]) -> None:
        self.value = list(deepcopy(value))
        super().__init__()

    @classmethod
    def from_any(cls, data: typing.Any) -> typing.Self:
        if not isinstance(data, typing.Iterable) or isinstance(data, str):
            raise OptionError(f"Expected iterable for Encounter Plando, got {type(data)}")
        plandos: list[PlandoEncounter] = []
        for plando in data:
            if isinstance(plando, PlandoEncounter):
                plandos.append(plando)
                continue
            if not isinstance(plando, typing.Mapping):
                raise OptionError(f"Expected Encounter Plando entries to be Mappings, got {type(plando)}")
            plando: typing.Mapping
            plando_casefold = {}
            for key in plando:
                casefold = str(key).casefold()
                if casefold not in ("map", "seasons", "season", "method", "slots", "slot", "species"):
                    raise OptionError(f"Unknown argument in Encounter Plando Entry: {str(key)}")
                if casefold in ("season", "slot"):
                    casefold += "s"
                if casefold in plando_casefold:
                    raise OptionError(f"Duplicate argument with different casing in Encounter Plando Entry: {str(key)}")
                plando_casefold[casefold] = plando[key]
            if "map" not in plando_casefold:
                raise OptionError("Encounter Plando entry is missing the map argument")
            if "method" not in plando_casefold:
                raise OptionError("Encounter Plando entry is missing the method argument")
            if "species" not in plando_casefold:
                raise OptionError("Encounter Plando entry is missing the species argument")
            map_ = plando_casefold["map"]
            seasons = plando_casefold.get("seasons", [])
            method = plando_casefold["method"]
            slots = plando_casefold.get("slots", [])
            species = plando_casefold["species"]
            # IMPORTANT strings are also Iterables
            if not isinstance(map_, str):
                raise OptionError(f"Expected map argument to be a string, got {type(map_)}")
            if isinstance(seasons, str):
                seasons = [seasons]
            elif isinstance(seasons, typing.Iterable):
                for season in seasons:
                    if not isinstance(season, str):
                        raise OptionError(f"Expected seasons argument to contain only strings, got {type(season)}")
            else:
                raise OptionError(f"Expected seasons argument to be a string or an iterable, got {type(seasons)}")
            if not isinstance(method, str):
                raise OptionError(f"Expected method argument to be a string, got {type(method)}")
            if isinstance(slots, int):
                slots = [slots]
            elif not isinstance(slots, typing.Iterable):
                raise OptionError(f"Expected slots argument to be an integer or an iterable, got {type(slots)}")
            else:
                for slot in slots:
                    if not isinstance(slot, int):
                        raise OptionError(f"Expected slots argument to contain only integers, got {type(slot)}")
            if isinstance(species, str):
                species = [species]
            elif not isinstance(species, typing.Iterable):
                raise OptionError(f"Expected species argument to be a string or an iterable, got {type(species)}")
            else:
                for spec in species:
                    if not isinstance(spec, str):
                        raise OptionError(f"Expected species argument to contain only strings, got {type(spec)}")
            plandos.append(PlandoEncounter(map_, seasons, method, slots, species))
        return cls(plandos)

    def verify(self, world: typing.Type["World"], player_name: str, plando_options: "PlandoOptions") -> None:
        if not settings.get_settings()["pokemon_bw_settings"]["enable_encounter_plando"]:
            self.value = []
            logging.warning(
                f"The encounter plando setting is turned off, so plandos for {player_name} will be ignored."
            )
            return
        try:
            self.verify_keys()
        except OptionError as validation_error:
            raise OptionError(f"Player {player_name} has invalid option keys:\n{validation_error}")

    def verify_keys(self) -> None:
        from .data.plando import encounter_maps
        from .data.pokemon.species import by_name

        invalid: list[str] = []
        for plando in self:
            reasons = []
            if plando.map not in encounter_maps.maps:
                reasons.append(f"Unknown map {plando.map}")
            for season in plando.seasons:
                if season.casefold() not in ("spring", "summer", "autumn", "winter"):
                    reasons.append(f"Unknown season {season}")
                if plando.map not in encounter_maps.multiple_seasons:
                    reasons.append(f"Map {plando.map} does not have multiple seasons")
            if plando.method.casefold() not in (
                "grass", "dark grass", "rustling grass", "surfing", "surfing rippling", "fishing", "fishing rippling"
            ):
                reasons.append(f"Unknown method {plando.method}")
            for slot in plando.slots:
                if slot >= 12 or slot < 0:
                    reasons.append(f"Slot {slot} out of bounds (0-11)")
                elif slot >= 5 and plando.method.casefold() not in ("grass", "dark grass", "rustling grass"):
                    reasons.append(f"Slot {slot} out of bounds for method {plando.method} (0-5)")
            if len(plando.species) == 0:
                reasons.append("No species provided")
            for species in plando.species:
                if species.casefold() != "none" and species not in by_name:
                    reasons.append(f"Unknown species {species}")
            if reasons:
                invalid.append(f"{plando.map}: " + ", ".join(reasons))
        if invalid:
            raise OptionError(
                f"Invalid Encounter Plando placement(s):\n" +
                "\n".join(invalid) +
                "\nRefer to the Text Plando guide of this game for further information."
            )

    def to_slot_data(self) -> list[dict[str, str | list[str] | list[int]]]:
        return [
            {
                "map": plando.map,
                "seasons": plando.seasons,
                "method": plando.method,
                "slots": plando.slots,
                "species": plando.species,
            }
            for plando in self
        ]

    @classmethod
    def get_option_name(cls, value: list[PlandoEncounter]) -> str:
        return str({
            f"{plando.map} ({', '.join(plando.seasons)}) - {plando.method} {plando.slots}": ", ".join(plando.species)
            for plando in value
        })

    def __iter__(self) -> typing.Iterator[PlandoEncounter]:
        yield from self.value

    def __getitem__(self, index: typing.SupportsIndex) -> PlandoEncounter:
        return self.value[index]

    def __len__(self) -> int:
        return len(self.value)


class RandomizeBaseStats(CasefoldOptionSet):
    """
    Randomizes the base stats of every pokemon species.
    - **Randomize** - Toggles base stats being randomized. Required for any other modifier.
    - **Keep total** - Every species will keep the sum of its base stats.
    - **Follow evolutions** - Evolved species will use their pre-evolution's base stats and add on top of that.
    """
    display_name = "Randomize Base Stats"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "Keep total",
        "Follow evolutions",
    ]
    default = []


class RandomizeEvolutions(CasefoldOptionSet):
    """
    Randomizes the evolutions of every pokemon species.
    - **Randomize** - Toggles evolutions being randomized. Required for any other modifier.
    - **Keep method** - Keeps the method (e.g. levelup, evolution stone, ...) of every evolution.
    - **Follow type** - Pre-evolution and evolved pokemon always share at least one type.
    - **Allow multiple pre-evolutions** - Multiple pokemon species can evolve into the same species.
    - **Allow more or less branches** - Allows all species to be able to evolve into more or less species than before.
    """
    display_name = "Randomize Evolutions"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "Keep method",
        "Follow type",
        "Allow multiple pre-evolutions",
        "Allow more or less branches",
    ]
    default = []


class RandomizeCatchRates(CasefoldOptionSet):
    """
    Randomizes the catch rate of every pokemon species.
    - **Shuffle** - Gives every species a commonly used catch rate (e.g. 255, 45, 3, ...).
    - **Randomize** - Gives every species a completely random catch rate. Overrides **Shuffle**.
    - **Follow evolutions** - Evolved species will have a catch rate equal to or lower than their pre-evolution(s).
    """
    display_name = "Randomize Catch Rates"
    valid_keys_casefold = True
    valid_keys = [
        "Shuffle",
        "Randomize",
        "Follow evolutions",
    ]
    default = []


class RandomizeLevelUpMovesets(CasefoldOptionSet):
    """
    Randomizes the moves a pokemon species learns by leveling up.
    - **Randomize** - Toggles level up movesets being randomized. Required for any other modifier.
    - **Keep types** - Randomized moves have either a matching or normal type.
    - **Progressive power** - If a move is learned after another one, it will have an equal or higher base power.
    - **Keep amount** - Keeps the amount of moves a species learns normally.
    - **Keep levels** - If the species learned a move at a certain level, it will still learn something at that level.
    - **Follow evolutions** - Evolved species will have at least 50% of the level up moveset(s) of their pre-evolution(s). Overrides all **Keep ...** modifiers.
    """
    display_name = "Randomize Level Up Movesets"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "Keep types",
        "Progressive power",
        "Keep amount",
        "Keep levels",
        "Follow evolutions",
    ]
    default = []


class RandomizeTypes(CasefoldOptionSet):
    """
    Randomizes the type(s) of every pokemon species.
    - **Randomize** - Toggles types being randomized. Required for any other modifier.
    - **Only secondary type** - Only randomizes the secondary type of every species and thereby keeps the primary type. Includes removing it. Not compatible with **Only primary type**.
    - **Only primary type** - Only randomizes the primary type of every species and thereby keeps the secondary type (which might be none). Not compatible with **Only secondary type**.
    - **Follow evolutions** - Evolved species will share at least one type with (one of) their pre-evolutions.
    """
    display_name = "Randomize Types"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "Only secondary type",
        "Only primary type",
        "Follow evolutions",
    ]
    default = []


class RandomizeAbilities(CasefoldOptionSet):
    """
    Randomizes the abilities of every pokemon species.
    - **Randomize** - Toggles abilities being randomized. Required for any other modifier.
    - **One per pokemon** - Gives every species only one ability.
    - **Follow evolutions** - Evolved pokemon will have the abilities of (one of) their pre-evolution(s)..
    - **Include hidden abilities** - Includes hidden abilities being randomized. Note that only a few select pokemon that originate from these games can have their hidden ability.
    """
    display_name = "Randomize Abilities"
    valid_keys_casefold = True
    valid_keys = [
        "Randomize",
        "One per pokemon",
        "Follow evolutions",
        "Include hidden abilities",
    ]
    default = []


class RandomizeGenderRatio(CasefoldOptionSet):
    """
    Randomizes the gender ratio of every pokemon species.
    - **Shuffle** - Gives every species a commonly used gender ratio (e.g. 50/50, 1 in 8, ...).
    - **Randomize** - Gives every species a completely random gender ratio. Overrides **Shuffle**.
    - **Follow evolutions** - Evolved species will have the same gender ratio as (one of) their pre-evolution(s).
    """
    display_name = "Randomize Gender Ratio"
    valid_keys_casefold = True
    valid_keys = [
        "Shuffle",
        "Randomize",
        "Follow evolutions",
    ]
    default = []


class RandomizeTMHMCompatibility(CasefoldOptionSet):
    """
    Randomizes the TM and HM compatibility of every pokemon species.
    - **Force all TMs** - Forces all TMs to be compatible with every pokemon species.
    - **Force all HMs** - Forces all HMs (and TM70 Flash) to be compatible with every pokemon species.
    - **Randomize** - Toggles TM and HM compatibility being randomized. Required for any other modifier.
    - **Keep types** - Randomized moves have either a matching or normal type.
    - **Keep amount** - Keeps the amount of moves a species learns normally.
    - **Follow evolutions** - Evolved species will have at least 50% of the learnable TMs and HMs of their pre-evolution(s). Overrides all **Keep ...** modifiers.
    """
    display_name = "Randomize TM/HM Compatibility"
    valid_keys_casefold = True
    valid_keys = [
        "Force all TMs",
        "Force all HMs",
        "Randomize",
        "Keep types",
        "Keep amount",
        "Follow evolutions",
    ]
    default = []


class StatsRandomizationAdjustments(ExtendedOptionCounter):
    """
    Adjust various parameters in various randomization options (more modifiers are planned).
    Any minimum parameter cannot be higher than its corresponding maximum parameter.

    """
    # **Randomize Base Stats:**
    # - **Stats total minimum/maximum** - The minimum/maximum base stats total, if randomized.
    #                                     Allowed values are integers in range 6 to 1530.

    # **Randomize Catch Rates:**
    # - **Catch rates minimum** - The minimum catch rates, if randomized.
    #                             Allowed values are integers in range 3 to 255.
    # - **Catch rates maximum** - The maximum catch rates, if randomized.
    #                             Allowed values are integers in range 3 to 255.

    # **Randomize Gender Ratio:**
    # - **Gender ratio minimum** - The minimum gender ratio, if randomized.
    #                              Allowed values are integers in range 0 to 255.
    #                              A gender ratio of 0 is always female and 255 is always male.
    # - **Gender ratio maximum** - The maximum gender ratio, if randomized.
    #                              A gender ratio of 0 is always female and 255 is always male.
    display_name = "Stats Randomization Adjustments"
    valid_keys = [
        # "Stats total minimum",
        # "Stats total maximum",
        # "Catch rates minimum",
        # "Catch rates maximum",
        # "Gender ratio minimum",
        # "Gender ratio maximum",
    ]
    default = {
        # "Stats total minimum": 6,
        # "Stats total maximum": 1530,
        # "Catch rates minimum": 3,
        # "Catch rates maximum": 255,
        # "Gender ratio minimum": 0,
        # "Gender ratio maximum": 255,
    }
    individual_min_max = {
        # "Stats total minimum": (6, 1530),
        # "Stats total maximum": (6, 1530),
        # "Catch rates minimum": (3, 255),
        # "Catch rates maximum": (3, 255),
        # "Gender ratio minimum": (0, 255),
        # "Gender ratio maximum": (0, 255),
    }


class ShuffleBadgeRewards(Choice):
    """
    Determines how gym badges are randomized and what items gym badge locations can have.
    This option might not be entirely strict (depending on other options and worlds).
    - **Vanilla** - Gym badges will stay at their vanilla locations.
    - **Shuffle** - Gym badges are shuffled between the gym leaders.
    - **Any badge** - Puts the badges into the item pool, while only allowing items that have the word "badge" in their name (which also applies to gym badges of other games/worlds) being placed at gym leaders.
    - **Anything** - Gym badges can be anywhere and gym leaders can give any item.
    """
    display_name = "Shuffle Badge Rewards"
    option_vanilla = 0
    option_shuffle = 1
    option_any_badge = 2
    option_anything = 3
    default = 1


class ShuffleTMRewards(Choice):
    """
    Determines what items NPCs, who would normally give TMs or HMs, can have.
    This option might not be entirely strict (depending on other options and worlds).
    - **Shuffle** - These NPCs will always give a TM or HM from the same world.
    - **HM with Badge** - Like "Shuffle", but puts each HM (and TM70 Flash) at a gym leader's badge reward (including the TM from Clay on route 6).
    - **Any TM/HM** - These NPCs will give any item that starts with "TM" or "HM" followed by any digit (which also applies to TMs and HMs of other games/worlds).
    - **Anything** - No restrictions.
    """
    display_name = "Shuffle TM Rewards"
    option_shuffle = 0
    option_hm_with_badge = 1
    option_any_tm_hm = 2
    option_anything = 3
    default = 0


class ShuffleRoadblockReqs(Toggle):
    """
    Roadblocks always require a specific item to disappear in this randomizer.
    If set to true, roadblocks will require a random key item.
    """
    display_name = "Shuffle Roadblock Requirements"
    default = False


class AdditionalRoadblocks(Choice):
    """
    Adds a number of additional roadblocks like cut trees or npcs blocking your way across the region.
    """
    display_name = "Additional Roadblocks"
    option_none = 0
    option_some = 1
    option_many = 2
    default = 0


class Dexsanity(Range):
    """
    Adds a number of locations that can be checked by catching a certain pokemon species
    and registering it in the pokedex. The actual maximum number of added checks depends on what pokemon species are
    actually obtainable in the wild.

    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.
    """
    display_name = "Dexsanity"
    default = 0
    range_start = 0
    range_end = 649


class Trainersanity(Range):
    """
    Adds a number of locations that can be checked by defeating a regular trainer.
    """
    display_name = "Trainersanity"
    default = 0
    range_start = 0
    range_end = 1  # TODO need to count trainers in the game


class Seensanity(Range):
    """
    Adds a number of locations that can be checked by seeing a certain Pokemon species, which is marked in the pokedex.
    The actual maximum number of added checks depends on what pokemon species are
    actually observable in the wild or in trainer battles.

    If you want to have all 649 possible checks, then you need to randomize wild
    encounters and add the **Ensure all obtainable** modifier.
    """
    display_name = "Seensanity"
    default = 0
    range_start = 0
    range_end = 649


class DoorShuffle(CasefoldOptionSet):
    """
    Shuffles or randomizes door warps.
    - **Gates** - Shuffles city gate entrances, leading to the region having a different layout than normally.
    - **Buildings per map** - Shuffles the building entrances (not gates) within every city or route.
    - **Buildings anywhere** - Shuffles building entrances (not gates) all over Unova.
    - **Dungeons** - Shuffles the location of all dungeons with two entrances and all dungeons with only one entrance.
    - **Full** - Fully shuffle all door warps. Overrides all modifiers above.
    - **Decoupled** - Removes the requirement for all shuffled door warps leading to each other.
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
    - **Vanilla** - Seasons are not randomized and change based on real time. Locations that depend on the season will only contain filler items.
    - **Changeable** - The current season can be changed by an NPC next to the Pokemon Center in Nimbasa City.
    - **Randomized** - All seasons are unlockable by items that get shuffled into the item pool. They can as well be changed by an NPC in Nimbasa City, with one season being unlocked from the beginning.
    """
    display_name = "Season Control"
    option_vanilla = 0
    option_changeable = 1
    option_randomized = 2
    default = 0


class AdjustLevels(CasefoldOptionSet):
    """
    Adjusts the levels of wild and trainer pokemon in areas that are in AP earlier accessible than in vanilla
    to not be significantly higher than in surrounding areas (regardless of randomization).

    - **Wild** - Normalizes wild pokemon levels, including surfing and fishing encounters.
    - **Trainer** - Normalizes trainer pokemon levels, excluding Cynthia.
    """
    display_name = "Adjust levels"
    valid_keys_casefold = True
    valid_keys = [
        "Wild",
        "Trainer",
        # "Static",
    ]
    default = ["Wild", "Trainer"]


class ModifyLevels(OptionCounter):
    """
    Modifies the level of all trainer and/or wild pokemon. You can choose a certain mode for each type of encounter.
    This is applied **after Adjust Levels**.
    The mode decides how to apply the value to every pokemon. You can write either the name of the mode
    or the corresponding number:
    - **Multiply** or **0** - Multiply each level with value being seen as a percentage, i.e. 100 means no modifying. Allowed values are in range 1 to 10000.
    - **Add** or **1** - Add the value directly to each level (with negative values being allowed), i.e. 0 means no modifying. Allowed values are in range -99 to 99.
    - **Power** or **2** - Raise each level to the power of the value (which is seen as a percentage), i.e. 100 means no modifying. Allowed values are in range 1 to 700.

    An alternative way with more capabilities is to write this as a list with multiple key names (like most plando options).
    Every entry must include the keys `type`, `mode`, and `value`.
    All entries are individual calculations that are applied one after another. Be aware of rounding errors.
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


class ExpModifier(Range):
    """
    Multiplies the experience received from defeating wild and trainer pokemon.

    The value is in percent, meaning 100 is normal, 200 is double, 50 is half, etc.
    """
    display_name = "Experience Modifier"
    default = 100
    range_start = 10
    range_end = 1600


class AllPokemonSeen(Toggle):
    """
    Marks all pokemon in the pokedex (that do not have a Seensanity check) as seen
    (including all forms, except shinies). This could possibly have no effect under certain circumstances.
    """
    display_name = "All Pokemon Seen"
    default = False


class AddFairyType(Choice):
    """
    Adds the fairy type from the sixth generation games.
    - **No** - Don't add the fairy type.
    - **Only randomized** - If types are randomized, this adds the fairy type to the pool of possible types.
    - **Modify vanilla** - Updates the type combination of all pokemon that received the fairy type in X and Y.
    """
    display_name = "Add Fairy Type"
    option_no = 0
    option_only_randomized = 1
    option_modify_vanilla = 2
    default = 0


class ReplaceEvoMethods(CasefoldOptionSet):
    """
    Replaces certain vanilla evolution methods with other methods that are easier to achieve.
    This also excludes them from randomized evolutions.
    Trade and time based evolutions are always replaced/excluded.

    - **Locations** - Replaces evolutions requiring a magnetic place, the ice rock, or the mossy rock with using a thunder stone, using a leaf stone, and leveling up with a held casteliacone.
    - **Friendship** - Replaces friendship based evolutions with level up evolutions.
    - **PID** - Replaces personality value based evolutions. Gender dependant evolutions lose their gender dependency, Wurmple's random evolutions will require a Butterfree/Venomoth in your party, and Burmy will also evolve into Mothim while having a Venomoth in your party. Be aware that this can lead to affected pokemon changing their gender when evolved.
    - **Stats** - Replaces Tyrogue's stat based evolutions with level up while holding a protein, iron, or carbos.
    """
    display_name = "Replace Evolution Methods"
    valid_keys_casefold = True
    valid_keys = [
        "Locations",
        "Friendship",
        "PID",
        "Stats",
    ]
    default = []


class MasterBallSeller(CasefoldOptionSet):
    """
    Adds the possibility to buy or obtain an unlimited amount of Master Balls.
    You can select multiple sellers.
    If multiple cost modifiers are added, a random cost in range between them (snapped to 500-steps) gets selected.
    Adding no cost modifier defaults to 3000.

    - **Ns Castle** - Repurposes an NPC in N's Castle, who can be found in the same room as the grunt giving Ultra Balls to the player, to give/sell Master Balls to the player.
    - **PC** - Adds an option to every PC in Pokémon Centers to buy/obtain Master Balls.
    - **Cherens Mom** - Repurposes Cheren's Mom in Nuvema Town to give/sell Master Balls.
    - **Undella Mansion seller** - Adds the Master Ball to the pool of items that you can buy from the evolution items seller in the Undella Mansion for a random price. His offers are not affected by any cost modifier.
    - **Cost Free** - Makes Master Balls (potentially) cost nothing.
    - **Cost x** - Makes Master Balls (potentially) cost x Pokédollars. x can be any number in range of 0 to 30000.
    """
    display_name = "Master Ball Seller"
    valid_keys_casefold = True
    valid_keys = [
        "Ns Castle",
        "PC",
        "Cherens Mom",
        "Undella Mansion seller",
        "Cost Free",
        "Cost 1000",
        "Cost 3000",
        "Cost 10000",
    ]
    default = []

    def __init__(self, value: typing.Iterable[str]):
        compatible = set()
        for val in value:
            if val in ("Cost: Free", "Cost: 1000", "Cost: 3000", "Cost: 10000"):
                compatible.add(val.replace(":", ""))
            elif val in ("N's Castle", "Cheren's Mom"):
                compatible.add(val.replace("'", ""))
            else:
                compatible.add(val)
        super().__init__(compatible)

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
    Adds pokemon to the item pool that can be obtained from an npc in [TBD] after receiving
    the corresponding item from another player. Pokemon will only be placed in other worlds and
    have a species that matches the theme of that world (if defined).
    """
    display_name = "Multiworld Gift Pokemon"
    default = False


class TrapsProbability(Range):
    """
    Determines the probability of every randomly generated filler item being replaced by a random trap item.
    """
    display_name = "Traps Probability"
    default = 0
    range_start = 0
    range_end = 100


class ModifyItemPool(CasefoldOptionSet):
    """
    Modifies what items your world puts into the item pool.

    - **Useless key items** - Adds one of each unused key item with filler classification.
    - **Useful filler** - Main bag items that would normally occur only once can be generated multiple times.
    - **Ban bad filler** - Bans niche berries and mail from being generated as filler items.
    """
    display_name = "Modify Item Pool"
    valid_keys_casefold = True
    valid_keys = [
        "Useless key items",
        "Useful filler",
        "Ban bad filler",
    ]
    default = []


class ModifyLogic(CasefoldOptionSet):
    """
    Modifies parts of what's logically required for various locations.

    - **Require Dowsing Machine** - Makes the Dowsing Machine a logical requirement to find hidden items.
    - **Prioritize key item locations** - Marks locations, that normally contain key items (which also includes
                                          badge rewards in gyms), as priority locations, making them mostly contain
                                          progressive items.
    - **Require Flash** - Makes Mistralton Cave, Challenger's Cave, and the basement of Wellspring Cave
                          logically require TM70 Flash.
    """
    display_name = "Modify Item Pool"
    valid_keys_casefold = True
    valid_keys = [
        "Require Dowsing Machine",
        "Prioritize key item locations",
        "Require Flash",
    ]
    default = ["Require Dowsing Machine", "Prioritize key item locations", "Require Flash"]


class FunnyDialog(Toggle):
    """
    Adds humorous dialogue submitted by the folks in the Pokemon Black and White thread of the
    Archipelago Discord server. This option requires Text Plando being enabled in the host settings.
    """
    display_name = "Funny Dialogue"
    default = 0


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
    # TODO definitely not done
    display_name = "Text Plando"
    default = [
        # ("story 160 0 7", "[vMisc_0] received [vPkmn_1]![NextLine] Congratulations![Terminate]", 100),
        # ("system 172 0 1", "Huh? Why did you press the[NextLine]B button?[Terminate]", 100),
    ]

    def verify_keys(self) -> None:
        invalid = []
        for word in self:
            parts = word.at.casefold().split()
            reasons = []
            if len(parts) < 4:
                reasons.append("Not enough arguments")
            if len(parts) > 4:
                reasons.append("Too many arguments")
            if parts[0] not in ("system", "story"):
                reasons.append("Unknown module")
            if not parts[1].isnumeric():
                reasons.append("File index is not a number")
            if not parts[2].isnumeric():
                reasons.append("Part index is not a number")
            if not parts[3].isnumeric():
                reasons.append("Line index is not a number")
            if reasons:
                invalid.append((" ".join(parts), reasons))
        if invalid:
            raise OptionError(
                f"Invalid \"at\" placement{'s' if len(invalid) > 1 else ''} " +
                f"in {getattr(self, 'display_name', self)}:\n" +
                "\n".join((f"{entry[0]}: {', '.join(entry[1])}" for entry in invalid)) +
                "\nRefer to the Text Plando guide of this game for further information."
            )


class ReusableTMs(Choice):
    """
    Enables reusable TMs, allowing for the reuse of TMs. 
    """
    display_name = "Reusable TMs"
    option_on = 0
    option_yes = 1
    option_of_course = 2
    option_im_not_a_masochist = 3
    default = 0

    @classmethod
    def from_text(cls, text: str) -> Choice:
        text = text.lower()
        if text in ("no", "off"):
            return cls(99)
        return super().from_text(text)

    @property
    def current_key(self) -> str:
        if self.value == 99:
            return "no"
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

    # Pokemon stats
    # randomize_base_stats: RandomizeBaseStats
    # randomize_evolutions: RandomizeEvolutions
    # randomize_level_up_movesets: RandomizeLevelUpMovesets
    # randomize_tm_hm_compatibility: RandomizeTMHMCompatibility
    # randomize_types: RandomizeTypes
    # randomize_abilities: RandomizeAbilities
    # randomize_catch_rates: RandomizeCatchRates
    # randomize_gender_ratio: RandomizeGenderRatio
    # stats_randomization_adjustments: StatsRandomizationAdjustments

    # Items, locations, and progression
    shuffle_badges: ShuffleBadgeRewards
    shuffle_tm_hm: ShuffleTMRewards
    # shuffle_roadblock_reqs: ShuffleRoadblockReqs
    # additional_roadblocks: AdditionalRoadblocks
    dexsanity: Dexsanity
    # trainersanity: Trainersanity
    # seensanity: Seensanity
    # door_shuffle: DoorShuffle
    season_control: SeasonControl

    # Miscellaneous
    adjust_levels: AdjustLevels
    modify_levels: ModifyLevels
    # exp_modifier: ExpModifier
    # all_pokemon_seen: AllPokemonSeen
    # add_fairy_type: AddFairyType
    # replace_evo_methods: ReplaceEvoMethods
    master_ball_seller: MasterBallSeller
    # deathlink: DeathLink  # Needs to be imported from base options
    # wonder_trade: WonderTrade
    # multiworld_gift_pokemon: MultiworldGiftPokemon
    # traps_percentage: TrapsPercentage
    modify_item_pool: ModifyItemPool
    modify_logic: ModifyLogic
    # funny_dialogue: FunnyDialog
    # text_plando: TextPlando
    reusable_tms: ReusableTMs
