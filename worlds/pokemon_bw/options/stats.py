import logging
import typing
from copy import deepcopy

import settings
from BaseClasses import PlandoOptions
from Options import OptionError, Option
from ..data.common_options import ToggleSet, ExtendedOptionCounter

if typing.TYPE_CHECKING:
    from worlds.AutoWorld import World


class RandomizeBaseStats(ToggleSet):
    """
    Randomizes the base stats of every pokemon species.
    You can add as many of the following modifiers as you want.

    - **Randomize** - Toggles base stats being randomized. Automatically added if any
        other modifier is added.
    - **Random total** - Allows the base stats of a species to be entirely random.
        Otherwise, the species will be roughly as strong as before.
    - **Follow evolutions** - Evolved species will use their pre-evolution's base stats
        and add on top of that.

    If evolutions are randomized and **Follow evolutions** is included, then not including **Random total** might
    not be followed consistently.
    """
    display_name = "Randomize Base Stats"
    is_randomize = False
    is_random_total = False
    is_follow_evolutions = False
    auto_add_if_any = "Randomize"


class RandomizeEvolutions(ToggleSet):
    """
    Randomizes the evolutions of every pokemon species.
    You can add as many of the following modifiers as you want.

    - **Randomize** - Toggles evolutions being randomized. Automatically added if any
        other modifier is added.
    - **Random methods** - Allows the method (e.g. levelup, evolution stone, ...) of
        every evolution to be randomized as well.
    - **Common type** - Pre-evolution and evolved pokemon always share at least one type.
    - **Follow type** - Whole evolution lines will share at least one type.
    - **Multiple pre-evolutions** - Different pokemon species can evolve into the same species.
    - **More or less branches** - Allows all species to be able to evolve into more or
        less different species than before.
    - **Looping evolution lines** - Allows all species to evolve into one of their
        pre-evolutions.
    - **Every level** - Makes all species only have a levelup evolution that triggers on
        any levelup. Including **More or less branches** will only ensure at least one
        method is levelup. This potentially ignores **Multiple pre-evolutions**,
        **Looping evolution lines**, and **Follow type** being excluded and
        **Random methods** being included.
    - **Pair stats** - Always makes the stats-dependent methods of Tyrogue be randomized together.
    - **Pair 50 50** - Always makes the PID-dependent methods of Wurmple be randomized together.
    - **Increasing stats** - Evolved pokemon will always have an equal or higher base
        stat total than their pre-evolutions.
    """
    display_name = "Randomize Evolutions"
    is_randomize = False
    is_random_methods = False
    is_common_type = False
    is_follow_type = False
    is_multiple_pre = False, "Multiple pre-evolutions"
    is_more_less_branches = False, "More or less branches"
    is_looping_lines = False, "Looping evolution lines"
    is_every_level = False
    is_pair_stats = False
    is_pair_50_50 = False
    is_increasing_stats = False
    auto_add_if_any = "Randomize"


class RandomizeTypes(ToggleSet):
    """
    Randomizes the type(s) of every pokemon species.
    You can add as many of the following modifiers as you want.

    - **Randomize** - Toggles types being randomized. Automatically added if any other
        modifier is added.
    - **Mono only** - All species will only get a single type.
    - **Dual only** - All species will only get two distinct types.
    - **Follow evolutions** - Evolved species will share at least one type with (one of)
        their pre-evolutions. Might not be fully ensured if combined with plando.
    - **Force evolutions** - Evolved species will have the exact same type(s) as
        (one of) their pre-evolutions. Might not be fully ensured if combined with
        plando. Supersedes **Follow evolutions**.
    - **Usual combinations** - Usual combinations in vanilla (e.g. Normal/Flying,
        Rock/Ground, ...) and more prominent mono types are more likely to show up.
    - **Permutation** - Each type will be replaced by a fixed other type, e.g. all Water
        types might be replaced with Flying types.

    Including both **Mono only** and **Dual only** will cancel each other out, i.e.
    it will be the same as including none of them.
    """
    display_name = "Randomize Types"
    is_randomize = False
    is_single_only = False, "Mono only"
    is_dual_only = False
    # is_only_secondary = False, "Only secondary type"
    # is_only_primary = False, "Only primary type"
    is_follow_evolutions = False
    is_force_evolutions = False
    is_usual_combinations = False
    is_permutation = False
    # is_no_4x_weaknesses = False
    auto_add_if_any = "Randomize"


class RandomizeCatchRates(ToggleSet):
    """
    Randomizes the catch rate of every pokemon species.
    You can add as many of the following modifiers as you want.

    - **Shuffle** - Gives every species a commonly used catch rate (e.g. 255, 45, 3, ...).
        Automatically added if any other modifier is added.
    - **Randomize** - Gives every species a completely random catch rate in range 3-255.
        Supersedes **Shuffle**.
    - **Follow evolutions** - Evolved species will have a catch rate equal to or lower
        than their pre-evolution(s).
    - **Correlate with base stats** - Species with a higher base stat total are more
        likely to have a lower catch rate.
    """
    display_name = "Randomize Catch Rates"
    is_shuffle = False
    is_randomize = False
    is_follow_evolutions = False
    is_correlate_with_base_stats = False
    auto_add_if_any = "Shuffle"


class RandomizeGenderRatio(ToggleSet):
    """
    Randomizes the gender ratio of every pokemon species.
    You can add as many of the following modifiers as you want.

    - **Shuffle** - Gives every species a commonly used gender ratio
        (e.g. 50/50, 1 in 8, ...).
    - **Randomize** - Gives every species a completely random gender ratio.
        Overrides **Shuffle**.
    - **Follow evolutions** - Evolved species will have the same gender ratio as (one of)
        their pre-evolution(s). Not including this can lead to some pokémon changing
        their gender when evolved.
    """
    display_name = "Randomize Gender Ratio"
    is_shuffle = False
    is_randomize = False
    is_follow_evolutions = False
    auto_add_if_any = "Shuffle"


class RandomizeLevelUpMovesets(ToggleSet):
    """
    Randomizes the moves a pokemon species learns by leveling up.
    You can add as many of the following modifiers as you want.

    - **Randomize** - Toggles level up movesets being randomized. Automatically added
        if any other modifier is added.
    - **Keep types** - Randomized moves have either a matching or normal type.
    - **Progressive power** - If a move is learned after another one (and it's not a
        status move), it will have an equal or higher base power.
    - **Keep amount** - Keeps the amount of moves a species learns normally.
    - **Keep levels** - If the species learned a move at a certain level, it will still
        learn something at that level.
    - **Follow evolutions** - Evolved species will try to have a large portion of the
        levelup moveset(s) of their pre-evolution(s). Has priority over some **Keep ...**
        modifiers. Might not be applied to all species if plando is used.
    - **Start with 4** - Ensures that each species learns at least 4 moves at level 1.
        Has priority over all **Keep ...** modifiers.
    """
    display_name = "Randomize Level Up Movesets"
    is_randomize = False
    is_keep_types = False
    is_progressive_power = False
    is_keep_amount = False
    is_keep_levels = False
    is_follow_evolutions = False
    is_start_with_4 = False
    auto_add_if_any = "Randomize"


class RandomizeTMHMCompatibility(ToggleSet):
    """
    Randomizes the TM and HM compatibility of every pokemon species.
    You can add as many of the following modifiers as you want.

    - **Force all TMs** - Forces all TMs to be compatible with every pokemon species.
    - **Force all HMs** - Forces all HMs (and TM70 Flash) to be compatible with every
        pokemon species.
    - **Randomize** - Toggles TM and HM compatibility being randomized. Required for any
        other modifier.
    - **Keep types** - Randomized moves have either a matching or normal type.
    - **Keep amount** - Keeps the amount of moves a species learns normally.
    - **Follow evolutions** - Evolved species will have at least 50% of the learnable TMs
        and HMs of their pre-evolution(s). Overrides all **Keep ...** modifiers.
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


class RandomizeAbilities(ToggleSet):
    """
    Randomizes the abilities of every pokemon species.
    You can add as many of the following modifiers as you want.

    - **Randomize** - Toggles abilities being randomized. Required for any other modifier.
    - **One per pokemon** - Gives every species only one ability.
    - **Follow evolutions** - Evolved pokemon will have the abilities of (one of) their
        pre-evolution(s).
    - **Include hidden abilities** - Includes hidden abilities being randomized.
        Note that only a few select pokemon that originate from these games can have
        their hidden ability.
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
    auto_add_if_any = "Randomize"


class RandomizeHeldItems(ToggleSet):
    """
    """
    display_name = "Randomize Held Items"
    is_randomize = False
    is_follow_evolutions = False
    is_no_1_percent = False
    is_no_5_percent = False
    auto_add_if_any = "Randomize"


class RandomizeEggGroups(ToggleSet):
    """
    """
    display_name = "Randomize Egg Groups"
    is_randomize = False
    is_keep_amount = False
    is_type_themed = False
    is_follow_evolutions = False
    auto_add_if_any = "Randomize"


class StatsRandomizationAdjustments(ExtendedOptionCounter):
    """
    Adjust various parameters in various randomization options.
    Any minimum parameter cannot be higher than its corresponding maximum parameter.
    Every parameter can be specified as unweighted/weighted lists, "random",
    and "random-range-x-y" like usual range options.

    - **Stats total minimum/maximum** (6-1530) - The minimum/maximum base stats total,
        if randomized.
    - **Levelup evo weight** (0-99) - If evolutions are randomized and **Random methods**
        is included, this will determine how likely it is to roll the levelup method.
        The lower this value, the more likely it is to get special methods (like using a
        stone, high friendship, ...). Setting this to -1 disables other methods.
    - **Maximum evo level** (10-100) - The maximum level at which levelup evolutions can occur.
    - **Catch rates minimum/maximum** (3-255) - The minimum/maximum catch rates, if randomized.
    - **Levelup moves amount minimum/maximum** (1-100) - The minimum/maximum amount of
        levelup moves a species can get, if randomized.
    """
    display_name = "Stats Randomization Adjustments"
    fill_defaults = True
    valid_keys = [
        "Stats total minimum",
        "Stats total maximum",
        "Level up evo weight",
        "Maximum evo level",
        "Catch rates minimum",
        "Catch rates maximum",
        "Levelup moves amount minimum",
        "Levelup moves amount maximum",
        # "Gender ratio minimum",
        # "Gender ratio maximum",
        # "No held item chance",
        # "Single egg group chance",
    ]
    default = {
        "Stats total minimum": 200,
        "Stats total maximum": 800,
        "Level up evo weight": 10,
        "Maximum evo level": 100,
        "Catch rates minimum": 3,
        "Catch rates maximum": 255,
        # "Gender ratio minimum": 0,
        # "Gender ratio maximum": 255,
        "Levelup moves amount minimum": 10,
        "Levelup moves amount maximum": 20,
        # "No held item chance": 90,
        # "Single egg group chance": 75,
    }
    individual_min_max = {
        "Stats total minimum": (6, 1530),
        "Stats total maximum": (6, 1530),
        "Level up evo weight": (-1, 99),
        "Maximum evo level": (10, 100),
        "Catch rates minimum": (3, 255),
        "Catch rates maximum": (3, 255),
        # "Gender ratio minimum": (0, 255),
        # "Gender ratio maximum": (0, 255),
        "Levelup moves amount minimum": (1, 100),
        "Levelup moves amount maximum": (1, 100),
        # "No held item chance": (0, 100),
        # "Single egg group chance": (0, 100),
    }
    min_max_pairs = [
        ("Stats total minimum", "Stats total maximum"),
        ("Catch rates minimum", "Catch rates maximum"),
        # ("Gender ratio minimum", "Gender ratio maximum"),
        ("Levelup moves amount minimum", "Levelup moves amount maximum"),
    ]


def plando_to_slotdata(value) -> typing.Any:
    if isinstance(value, dict):
        return {v: plando_to_slotdata(vv) for v, vv in value.items()}
    if isinstance(value, tuple) and hasattr(value, "_fields") and hasattr(value, "_asdict"):
        return {v: plando_to_slotdata(vv) for v, vv in value._asdict().items()}
    if not isinstance(value, str) and isinstance(value, typing.Iterable):
        return tuple(plando_to_slotdata(v) for v in value)
    return value


class PlandoEvolution(typing.NamedTuple):
    species: str
    method: str = "Level up"
    level: int = 20
    stone: str = "Shiny Stone"
    held: str = "King's Rock"
    move: str = "Toxic"
    partner: str = "Remoraid"
    species_2: str = "Shedinja"
    species_3: str = "Hitmontop"


class PlandoLevelupMove(typing.NamedTuple):
    move: str
    level: int


class PlandoStat(typing.NamedTuple):
    base_hp: int = 0
    base_attack: int = 0
    base_defense: int = 0
    base_sp_attack: int = 0
    base_sp_defense: int = 0
    base_speed: int = 0
    catch_rate: int = 0
    evolutions: list[PlandoEvolution] | bool = False
    override_evolutions: bool = True
    levelup_moveset: list[PlandoLevelupMove] | bool = False
    override_levelup_moveset: bool = True
    types: list[str] = []


class StatsPlando(Option[dict[str, PlandoStat]]):
    """
    Here you can change certain stats of a pokemon species to your liking.
    More stats are planned to be changeable.

    Here's an example of how this would look like:
    ```
    stats_plando:
      Bulbasaur:
        base_hp: 5
        base_attack: 5
        base_sp_attack: 255
        catch_rate: 190
        evolutions:
          - species: Squirtle
            method: Stone
            stone: Water Stone
          - species: Eevee
            method: Level up
            level: 30
        override_evolutions: false
        levelup_moveset:
          - move: Earthquake
            level: 1
          - move: Pound
            level: 100
        override_levelup_moveset: false
        types: [Fire, Electric]
    ```

    Stats Plando requires the corresponding host setting to be enabled, else it will be
    ignored for all players. Be aware that this can lead to generation failures when
    combined with other restrictive options or potential softlocks.
    Refer to the Stats Plando guide of this game for further information.
    """
    display_name = "Stats Plando"
    supports_weighting = False
    default = {}

    def __init__(self, value: dict[str, PlandoStat]) -> None:
        self.value = deepcopy(value)
        super().__init__()

    @classmethod
    def from_any(cls, data: dict) -> typing.Self:
        if not isinstance(data, dict):
            raise OptionError(f"Expected dictionary for Stats Plando, got {type(data)}")
        plandos: dict[str, PlandoStat] = {}
        for spec, plando in data.items():
            if not isinstance(spec, str):
                raise OptionError(f"Species name in Stats Plando expected to be a string, got {type(plando)}")
            if isinstance(plando, PlandoStat):
                plandos[spec] = plando
                continue
            if not isinstance(plando, dict):
                raise OptionError(f"Expected dictionary as Stats Plando entry {spec}, got {type(plando)}")
            plando_evolutions, plando_levelup_moves, plando_types = [], [], ()
            for plando_key, value in plando.items():
                if plando_key not in PlandoStat._fields:
                    raise OptionError(f"Unknown Stats Plando entry key: {plando_key}")
                if plando_key == "evolutions":
                    if not (isinstance(value, list) or value is False):
                        raise OptionError(f"Expected value of evolutions key to be a list or 'false', got {type(value)}")
                    for evo_entry in value:
                        if isinstance(evo_entry, PlandoEvolution):
                            plando_evolutions.append(evo_entry)
                            continue
                        if not isinstance(evo_entry, dict):
                            raise OptionError(f"Expected evolution entry to be a dictionary, got {type(evo_entry)}")
                        if "species" not in evo_entry:
                            raise OptionError(f"An evolution entry for species {spec} is missing the 'species' key")
                        for evo_entry_key in evo_entry:
                            if not isinstance(evo_entry_key, str):
                                raise OptionError(
                                    f"Evolution entry key expected to be a string, got {type(evo_entry_key)}")
                            if evo_entry_key not in PlandoEvolution._fields:
                                raise OptionError(f"Unknown evolution entry key: {evo_entry_key}")
                        plando_evolutions.append(PlandoEvolution(**evo_entry))
                if plando_key == "levelup_moveset":
                    if not (isinstance(value, list) or value is False):
                        raise OptionError(f"Expected value of levelup_moveset key to be a list or 'false', got {type(value)}")
                    for move_entry in value:
                        if isinstance(move_entry, PlandoLevelupMove):
                            plando_levelup_moves.append(move_entry)
                            continue
                        if not isinstance(move_entry, dict):
                            raise OptionError(f"Expected levelup move entry to be a dictionary, got {type(move_entry)}")
                        if "move" not in move_entry:
                            raise OptionError(f"A levelup move entry for species {spec} is missing the 'move' key")
                        if "level" not in move_entry:
                            raise OptionError(f"A levelup move entry for species {spec} is missing the 'level' key")
                        for move_entry_key in move_entry:
                            if not isinstance(move_entry_key, str):
                                raise OptionError(
                                    f"Levelup move entry key expected to be a string, got {type(move_entry_key)}")
                            if move_entry_key not in PlandoLevelupMove._fields:
                                raise OptionError(f"Unknown levelup move entry key: {move_entry_key}")
                        plando_levelup_moves.append(PlandoLevelupMove(**move_entry))
                if plando_key == "types":
                    if isinstance(value, list) or isinstance(value, tuple):
                        plando_types = list(value)
                    elif isinstance(value, str):
                        plando_types = [value]
                    else:
                        raise OptionError(f"Expected value of types key to be a list or string, got {type(value)}")
            plando["evolutions"] = plando_evolutions
            plando["levelup_moveset"] = plando_levelup_moves
            plando["types"] = plando_types
            plandos[spec] = PlandoStat(**plando)
        return cls(plandos)

    def verify(self, world: typing.Type["World"], player_name: str, plando_options: "PlandoOptions") -> None:
        if not settings.get_settings()["pokemon_bw_settings"]["enable_stats_plando"]:
            self.value = []
            logging.warning(
                f"The stats plando setting is turned off, so plandos for {player_name} will be ignored."
            )
            return
        try:
            self.verify_keys()
        except OptionError as validation_error:
            raise OptionError(f"Player {player_name} has invalid option keys:\n{validation_error}")

    def verify_keys(self) -> None:
        from ..data.pokemon.species import by_name as species_by_name
        from ..data.pokemon.pokedex import by_name as dex_by_name
        from ..data.pokemon.evolution_methods import methods as methods_table, paired_method_slots as paired_table, stone_items, hold_items
        from ..data.items import all_items_dict_view
        from ..data.pokemon.moves import by_name as move_by_name
        from ..data.pokemon.types import by_name as types_by_name

        invalid: list[str] = []
        for plando in self:
            reasons = []
            if plando[0] in species_by_name:
                spec_data = species_by_name[plando[0]]
                if spec_data.form and not spec_data.is_custom_form:
                    reasons.append(f"Species name is a form that cannot be edited")
            elif plando[0] not in dex_by_name:
                reasons.append(f"Unknown species name")
            plando_stat: PlandoStat = plando[1]
            if not isinstance(plando_stat.override_evolutions, int):
                reasons.append((f"override_evolutions value \"{plando_stat.override_evolutions}\" is neither "
                                f"a boolean nor an integer"))
            if not isinstance(plando_stat.override_levelup_moveset, int):
                reasons.append((f"override_levelup_moveset value \"{plando_stat.override_levelup_moveset}\" is neither "
                                f"a boolean nor an integer"))
            if not (isinstance(plando_stat.base_hp, int) and 0 <= plando_stat.base_hp <= 255):
                reasons.append(f"Base HP {plando_stat.base_hp} is not an integer in range 0-255")
            if not (isinstance(plando_stat.base_attack, int) and 0 <= plando_stat.base_attack <= 255):
                reasons.append(f"Base attack {plando_stat.base_attack} is not an integer in range 0-255")
            if not (isinstance(plando_stat.base_defense, int) and 0 <= plando_stat.base_defense <= 255):
                reasons.append(f"Base defense {plando_stat.base_defense} is not an integer in range 0-255")
            if not (isinstance(plando_stat.base_sp_attack, int) and 0 <= plando_stat.base_sp_attack <= 255):
                reasons.append(f"Base special attack {plando_stat.base_sp_attack} is not an integer in range 0-255")
            if not (isinstance(plando_stat.base_sp_defense, int) and 0 <= plando_stat.base_sp_defense <= 255):
                reasons.append(f"Base special defense {plando_stat.base_sp_defense} is not an integer in range 0-255")
            if not (isinstance(plando_stat.base_speed, int) and 0 <= plando_stat.base_speed <= 255):
                reasons.append(f"Base speed {plando_stat.base_speed} is not an integer in range 0-255")
            if not (isinstance(plando_stat.catch_rate, int) and (not plando_stat.catch_rate or
                                                                 3 <= plando_stat.catch_rate <= 255)):
                reasons.append(f"Catch rate {plando_stat.catch_rate} is neither 0 nor an integer in range 3-255")
            if len(plando_stat.types) > 2:
                reasons.append(f"A maximum of 2 types is allowed, not {len(plando_stat.types)}")
            for plando_type in plando_stat.types:
                if plando_type not in types_by_name:
                    reasons.append(f"{plando_type} is not an allowed type")
            evo_sum = 0
            if plando_stat.evolutions is not False:
                for plando_evo in plando_stat.evolutions:
                    if plando_evo.species not in species_by_name and plando_evo.species not in dex_by_name:
                        reasons.append(f"Unknown species name: {plando_evo.species}")
                    if plando_evo.partner not in species_by_name and plando_evo.partner not in dex_by_name:
                        reasons.append(f"Unknown partner pokémon name: {plando_evo.partner}")
                    if plando_evo.method not in methods_table and plando_evo.method not in paired_table:
                        reasons.append(f"Unknown evolution method: {plando_evo.method}")
                    evo_sum += paired_table.get(plando_evo.method, 1)
                    if not isinstance(plando_evo.level, int):
                        reasons.append(f"Evolution level is not an integer: {plando_evo.level}")
                    if not 2 <= plando_evo.level <= 100:
                        reasons.append(f"Evolution level {plando_evo.level} out of range, allowed are values in range 2-100")
                    if plando_evo.stone not in all_items_dict_view:
                        reasons.append(f"Unknown evolution stone item: {plando_evo.stone}")
                    if all_items_dict_view[plando_evo.stone].item_id not in stone_items:
                        reasons.append(f"Item {plando_evo.stone} is not an evolution stone")
                    if plando_evo.held not in all_items_dict_view:
                        reasons.append(f"Unknown evolution held item: {plando_evo.held}")
                    if all_items_dict_view[plando_evo.held].item_id not in hold_items:
                        reasons.append(f"Item {plando_evo.held} is not an evolution item")
                    if plando_evo.move not in move_by_name:
                        reasons.append(f"Unknown move: {plando_evo.move}")
                    if plando_evo.species_2 not in species_by_name and plando_evo.species_2 not in dex_by_name:
                        reasons.append(f"Unknown species name for key 'species_2': {plando_evo.species_2}")
                    if plando_evo.species_3 not in species_by_name and plando_evo.species_3 not in dex_by_name:
                        reasons.append(f"Unknown species name for key 'species_3': {plando_evo.species_3}")
            if evo_sum > 7:
                reasons.append(f"Too many evolution entries")
            if plando_stat.levelup_moveset is not False:
                any_1 = False
                for plando_move in plando_stat.levelup_moveset:
                    if plando_move.move not in move_by_name:
                        reasons.append(f"Unknown move name: {plando_move.move}")
                    if not isinstance(plando_move.level, int):
                        reasons.append(f"Move level is not an integer: {plando_move.level}")
                    if not 1 <= plando_move.level <= 100:
                        reasons.append(f"Move level {plando_move.level} out of range, allowed are values in range 1-100")
                    any_1 |= plando_move.level == 1
                if plando_stat.override_levelup_moveset and not any_1:
                    reasons.append(f"Overriding levelup moveset requires at least one move being learned at level 1")
            if reasons:
                invalid.append(f"{plando[0]}: " + ", ".join(reasons))
        if invalid:
            raise OptionError(
                f"Invalid Stats Plando placement(s):\n" +
                "\n".join(invalid) +
                "\nRefer to the Stats Plando guide of this game for further information."
            )

    def to_slot_data(self) -> list[dict[str, str | list[str] | list[int]]]:
        return plando_to_slotdata(self.value)

    @classmethod
    def get_option_name(cls, value: dict[str, PlandoStat]) -> str:
        return str(plando_to_slotdata(value))

    def __iter__(self) -> typing.Iterator[tuple[str, PlandoStat]]:
        yield from self.value.items()

    def __getitem__(self, index) -> PlandoStat:
        return self.value[index]

    def __len__(self) -> int:
        return len(self.value)
