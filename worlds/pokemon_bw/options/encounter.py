import logging
import typing
from copy import deepcopy

import settings
from BaseClasses import PlandoOptions
from Options import OptionSet, OptionError, Option
from ..data.common_options import ToggleSet, ExtendedOptionCounter
from ..data.pokemon import species

if typing.TYPE_CHECKING:
    from worlds.AutoWorld import World


class RandomizeWildPokemon(ToggleSet):
    """
    Randomizes wild pokemon encounters.
    You can add as many of the following modifiers as you want.

    The following is an example for how options like this can look like (when edited in a yaml):
    ```
    randomize_wild_pokemon:
        ["Randomize", "Prevent rare encounters"]
    ```
    Here is an alternative way to format it:
    ```
    randomize_wild_pokemon:
        - Randomize
        - Prevent rare encounters
    ```

    - **Randomize** - Toggles wild pokemon being randomized. Automatically added if any
        other modifier is added.
    - **Ensure all obtainable** - Ensures that every pokemon species is obtainable by
        either catching or evolving.
    - **Similar base stats** - Tries to keep every randomized pokemon at a similar base
        stat total as the replaced encounter.
    - **Prevent overpowered pokemon** - Tries to prevent pokemon with a base stat total
        over an adjustable threshold being randomized into wild encounter slots. Other
        modifiers (except for **Similar base stats**) take priority in case of conflicts.
    - **Prevent bad early pokemon** - Prevents encountering Wonder Guard and fixed HP
        attacks in regions that don't have at least level 20 encounters. Might not be
        fully ensured depending on other options.
    - **Type themed areas** - Tries to make every pokemon in an area have a certain same
        type. Might not be fully ensured depending on RNG.
    - **Area 1 to 1** - Keeps the amount of different encounters and their encounter rate
        in every area.
    - **Merge phenomenons** - Makes rustling grass, rippling water spots, dust clouds,
        and flying shadows in the same area have only one encounter. Takes priority over
        **Area 1 to 1**.
    - **Prevent rare encounters** - Randomizes the encounter slots with the lowest chance
        in each area to the same pokemon. Takes priority over **Area 1-to-1**.

    It is **highly recommended** to include **Prevent rare encounters** if you want to randomize wild pokemon,
    else you might find yourself searching for two 1% encounters on every route.
    """
    # **Ensure all obtainable** -  ... This is automatically checked if **National pokedex** is chosen as the goal.
    display_name = "Randomize Wild Pokemon"
    is_randomize = False
    is_ensure_all = False, "Ensure all obtainable"
    is_similar_stats = False, "Similar base stats"
    is_prevent_overpowered = False, "Prevent overpowered pokemon"
    is_prevent_bad_early = False, "Prevent bad early pokemon"
    is_type_themed_areas = False
    is_area_1_to_1 = False
    is_merge_phenomena = False
    is_prevent_rare = False, "Prevent rare encounters"
    auto_add_if_any = "Randomize"
    aliases_convert = [
        ("Area 1-to-1", "Area 1 to 1"),
        ("Area 1-1", "Area 1 to 1"),
        ("Merge phenomenons", "Merge phenomena"),
    ]


class RandomizeTrainerPokemon(ToggleSet):
    """
    Randomizes trainer pokemon.
    You can add as many of the following modifiers as you want.

    - **Randomize** - Toggles trainer pokemon being randomized. Automatically added if
        any other modifier is added.
    - **Similar base stats** - Tries to keep the randomized pokemon at a similar base
        stat total as the replaced one.
    - **Prevent overpowered pokemon** - Prevents trainers from having pokemon with a base
        stats total above an adjustable threshold. Takes priority over most other modifiers.
    - **Evolve when possible** - Tries to evolve pokemon if they are able to (based on
        their level). Pokémon that evolve independently of their level are evolved at level 25.
    - **Force fully evolved** - Always fully evolves pokemon above a certain (adjustable) level.
    - **Type themed** - All pokemon of a trainer will share at least one randomly chosen type.
    - **Themed gym trainers** - All pokemon of gym trainers will share the type assigned
        to their gym leader.
    - **Shuffle gym leader types** - Assigns a (unique) random type to each gym leader
        and elite 4 member instead of using their vanilla type. Do note that they always
        have type themed teams.
    - **Rivals keep starter** - Makes all Bianca/Cheren fights have one pokemon in
        common, which will always evolve when possible.
    """
    display_name = "Randomize Trainer Pokemon"
    is_randomize = False
    is_similar_stats = False, "Similar base stats"
    is_prevent_overpowered = False, "Prevent overpowered pokemon"
    is_evolve_possible = False, "Evolve when possible"
    is_force_evolved = False, "Force fully evolved"
    is_type_themed = False
    is_themed_gym_trainers = False
    is_shuffle_gym_types = False, "Shuffle gym leader types"
    is_rivals_keep_starter = False
    # is_themed_gym_trainers = False
    # Not sure whether I really want to implement these:
    # is_randomize_abilities = False
    # is_randomize_natures = False
    # is_randomize_held_items = False
    # is_only_already_held = False, "Only already with held item"
    # is_allow_no_held_item = False
    # is_randomize_unique = False, "Randomize unique moves"
    # is_themed_unique = False, "Only themed unique moves"
    auto_add_if_any = "Randomize"


class RandomizeStarterPokemon(ToggleSet):
    """
    Randomizes the starter pokemon you receive at the start of the game.
    You can add as many of the following modifiers as you want.

    - **Randomize** - Toggles starter pokemon being randomized. Automatically added if
        any other modifier is added.
    - **Any base** - Only use unevolved/baby pokemon.
    - **Base with 2 evolutions** - Only use unevolved/baby pokemon that can evolve twice.
        Overrides **Any base**.
    - **Only official starters** - Only use pokemon that have been a starter in any
        mainline game. Overrides **Any base** and **Base with 2 evolutions**.
    - **Type variety** - Every starter will have types that are different from the other two.
    """
    display_name = "Randomize Starter Pokemon"
    valid_keys = [
        "Randomize",
        "Any base",
        "Base with 2 evolutions",
        "Only official starters"
        "Type variety",
    ]
    default = []
    auto_add_if_any = "Randomize"


class RandomizeStaticPokemon(ToggleSet):
    """
    Randomizes static encounters you can battle and catch throughout the game,
    e.g. Volcarona in Relic Castle.
    You can add as many of the following modifiers as you want.

    - **Randomize** - Toggles static pokemon being randomized. Automatically added if any
        other modifier is added.
    - **Similar base stats** - Tries to keep the randomized pokemon at a similar base
        stat total as the replaced one.
    - **Only base** - Only use unevolved Pokemon.
    - **No legendaries** - Exclude legendaries from being placed into static encounters.
    - **Split statues** - Splits the statues in Desert Resort into 5 different species.
    """
    display_name = "Randomize Static Pokemon"
    valid_keys = [
        "Randomize",
        "Similar base stats",
        "Only base",
        "No legendaries",
        "Split statues",
    ]
    default = []
    auto_add_if_any = "Randomize"


class RandomizeGiftPokemon(ToggleSet):
    """
    Randomizes gift pokemon that you receive for free, e.g. the Larvesta egg on route 18.
    You can add as many of the following modifiers as you want.

    - **Randomize** - Toggles gift pokemon being randomized. Automatically added if any
        other modifier is added.
    - **Similar base stats** - Tries to keep the randomized pokemon at a similar base
        stat total as the replaced one.
    - **No legendaries** - Exclude legendaries from being placed into gift encounters.
    - **Split monkeys** - Makes the gift encounter in Dreamyard depend on which starter
        you picked (like in vanilla), else it will always give you the same species.
    """
    display_name = "Randomize Gift Pokemon"
    valid_keys = [
        "Randomize",
        "Similar base stats",
        "No legendaries",
        "Split monkeys",
    ]
    default = []
    auto_add_if_any = "Randomize"


class RandomizeTradePokemon(ToggleSet):
    """
    Randomizes trade offers from NPCs. Any **Randomize ...** is required for the
    other modifiers.
    You can add as many of the following modifiers as you want.

    - **Randomize offer** - Toggles offered pokemon being randomized.
    - **Randomize request** - Toggles requested pokemon being randomized.
    - **Similar base stats** - Tries to keep the randomized pokemon at a similar base
        stat total as the replaced one.
    - **Coupled base stats** - Tries to make offered and requested pokemon have similar
        base stats.
    - **No legendaries** - Exclude legendaries from being placed into trades.
    """
    display_name = "Randomize Trade Pokemon"
    valid_keys = [
        "Randomize offer",
        "Randomize request",
        "Similar base stats",
        "Coupled base stats",
        "No legendaries",
    ]
    default = []


class RandomizeLegendaryPokemon(ToggleSet):
    """
    Randomizes legendary and mythical encounters.
    You can add as many of the following modifiers as you want.

    - **Randomize** - Toggles legendary pokemon being randomized. Automatically added if
        any other modifier is added.
    - **Keep legendary** - Randomized pokemon will all still be legendaries or mythicals.
    - **No legendaries** - Exclude legendaries from being placed into these encounters.
    - **Similar base stats** - Tries to keep the randomized pokemon at a similar base
        stat total as the replaced one. Overrides **Keep legendary**.
    - **Same type** - Tries to keep at least one type of every encounter.

    Including **Keep legendary** AND **No legendaries** will instead only put pseudo
    legendaries into these encounters.
    """
    display_name = "Randomize Legendary Pokemon"
    valid_keys = [
        "Randomize",
        "Keep legendary",
        "No legendaries",
        "Similar base stats",
        "Same type",
    ]
    default = []
    auto_add_if_any = "Randomize"


class PokemonRandomizationAdjustments(ExtendedOptionCounter):
    """
    Adjust various parameters in various pokemon randomization options
    (with individual ranges).
    Every parameter can be specified as unweighted/weighted lists, "random",
    and "random-range-x-y" like usual range options.

    - **Stats leniency** (0-1530) - The starting maximum difference between base stat
        totals of vanilla and randomized species (for options with **Similar base stats**
        activated).
    - **Rare encounters threshold** (1-100) - If **Prevent rare encounters** is included,
        this will be the minimum encounter chance (in percent) for each species.
    - **Overpowered threshold** (200, 1530) - The maximum base stat total (for options
        with **Prevent overpowered pokemon** activated).
    - **Force evolutions threshold** (1, 100) - The minimum level at which trainer
        pokemon are forced to be fully evolved (if **Force fully evolved** is included).
    """
    display_name = "Pokemon Randomization Adjustments"
    fill_defaults = True
    valid_keys = [
        "Stats leniency",
        "Rare encounters threshold",
        "Overpowered threshold",
        "Force evolutions threshold",
    ]
    default = {
        "Stats leniency": 10,
        "Rare encounters threshold": 8,
        "Overpowered threshold": 500,
        "Force evolutions threshold": 40,
    }
    individual_min_max = {
        "Stats leniency": (0, 1530),
        "Rare encounters threshold": (1, 100),
        "Overpowered threshold": (200, 1530),
        "Force evolutions threshold": (1, 100),
    }


def plando_to_slotdata(value) -> typing.Any:
    if isinstance(value, dict):
        return {v: plando_to_slotdata(vv) for v, vv in value.items()}
    if isinstance(value, tuple) and hasattr(value, "_fields") and hasattr(value, "_asdict"):
        return {v: plando_to_slotdata(vv) for v, vv in value._asdict()}
    if not isinstance(value, str) and isinstance(value, typing.Iterable):
        return tuple(plando_to_slotdata(v) for v in value)
    return value


class PlandoEncounter(typing.NamedTuple):
    map: str
    seasons: list[str]
    method: str
    slots: list[int]
    species: list[str]


class EncounterPlando(Option[list[PlandoEncounter]]):
    """
    Places specific pokemon species at specific locations.

    Every entry follows the following format:
    ```
    - map: Name of map
      seasons: Season name(s), optional
      method: Grass/Dark grass/...
      slots: Slot number(s) (0-11), optional
      species: Name(s) of species, random if multiple
    ```
    Encounter Plando requires the corresponding host setting to be enabled, else it will
    be ignored for all players. Be aware that this can lead to generation failures when
    combined with other restrictive options.
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
        from ..data.plando import encounter_maps
        from ..data.pokemon.species import by_name

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
                "\nRefer to the Encounter Plando guide of this game for further information."
            )

    def to_slot_data(self) -> list[dict[str, str | list[str] | list[int]]]:
        return plando_to_slotdata(self.value)

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


class WildRandomizationBlacklist(OptionSet):
    """
    Excludes a list of pokemon from being used in wild randomization.
    Be aware that certain pokemon still have to be encountered somewhere, especially with
    **Ensure all obtainable** enabled. Also, a big list can lead to generation failures.
    """
    display_name = "Wild Randomization Blacklist"
    valid_keys = list(species.by_name)


class TrainerRandomizationBlacklist(OptionSet):
    """
    Excludes a list of pokemon from being used in trainer randomization.
    Be aware that a big list can lead to generation failures.
    """
    display_name = "Wild Randomization Blacklist"
    valid_keys = WildRandomizationBlacklist.valid_keys
